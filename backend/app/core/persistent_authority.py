from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from bson import ObjectId

from ..models.revision import RevisionNodeModel, RevisionMetadata, RevisionStatus, PartChange, ChangeType
from .database import mongodb
from .transaction import transaction_manager
from ..models import revision

logger = logging.getLogger(__name__)

class PersistentAuthorityEngine:
    """
    Authority engine with persistent storage.
    Can reconstruct state from database at any time.
    """
    
    def __init__(self):
        self._graph_cache: Dict[str, Dict[str, RevisionNodeModel]] = {}  # document_id -> {revision -> node}
        self._initialized = False
    
    async def initialize(self):
        """Reconstruct graph from database on startup"""
        db = mongodb.db
        
        # Load semua revisions
        cursor = db.revisions.find().sort("created_at", 1)
        revisions = await cursor.to_list(length=None)
        
        for rev_data in revisions:
            rev = RevisionNodeModel(**rev_data)
            
            if rev.document_id not in self._graph_cache:
                self._graph_cache[rev.document_id] = {}
            
            self._graph_cache[rev.document_id][rev.revision] = rev
        
        self._initialized = True
        logger.info(f"✅ Authority engine initialized with {sum(len(g) for g in self._graph_cache.values())} revisions")
    
    async def _find_previous_revision(self, document_id: str, current_rev: str) -> Optional[ObjectId]:
        """Cari revisi sebelumnya berdasarkan numbering convention"""
        db = mongodb.db
        
        # Parse revision number (030.4 → 030.3)
        try:
            if '.' in current_rev:
                major, minor = current_rev.split('.')
                prev_minor = int(minor) - 1
                if prev_minor >= 0:
                    candidate = f"{major}.{prev_minor}"
                    
                    # Cari di cache dulu
                    if document_id in self._graph_cache and candidate in self._graph_cache[document_id]:
                        return self._graph_cache[document_id][candidate].id
                    
                    # Cari di database
                    prev = await db.revisions.find_one({
                        "document_id": document_id,
                        "revision": candidate
                    })
                    if prev:
                        return prev["_id"]
        except:
            pass
        
        # Fallback: ambil revision terakhir
        last = await db.revisions.find_one(
            {"document_id": document_id},
            sort=[("created_at", -1)]
        )
        if last:
            return last["_id"]
        
        return None
    
    async def register_revision(self, 
                                document_id: str,
                                document_number: str,
                                revision: str,
                                parts: List[Dict],
                                issue_date: Optional[datetime] = None,
                                source_pdf_path: Optional[str] = None,
                                file_hash: Optional[str] = None,
                                created_by: str = "system") -> RevisionNodeModel:
        """Register new revision atomically"""

        # Cari previous revision
        previous_id = await self._find_previous_revision(document_id, revision)

        # Hitung changes
        changes = await self._compute_changes(document_id, previous_id, parts)

        # Konversi PartChange ke dict
        changes_dict = []
        for c in changes:
            c_dict = {
                "part_number": c.part_number,
                "change_type": c.change_type.value,
                "fields_changed": c.fields_changed
            }
            if c.old_value:
                c_dict["old_value"] = c.old_value
            if c.new_value:
                c_dict["new_value"] = c.new_value
            changes_dict.append(c_dict)

        # Buat change summary
        change_summary = {
            "type": "UPDATE" if previous_id else "INITIAL",
            "added_parts": [c.part_number for c in changes if c.change_type == ChangeType.ADD],
            "removed_parts": [c.part_number for c in changes if c.change_type == ChangeType.DELETE],
            "modified_parts": changes_dict,
            "total_parts": len(parts)
        }

        # Buat metadata
        metadata = RevisionMetadata(
            created_by=created_by,
            created_at=datetime.utcnow(),
            status=RevisionStatus.DRAFT
        )

        # Buat revision node
        rev_node = RevisionNodeModel(
            document_id=document_id,
            document_number=document_number,
            revision=revision,
            parts=parts,
            part_count=len(parts),
            change_summary=change_summary,
            changes=changes_dict,
            issue_date=issue_date,
            source_pdf_path=source_pdf_path,
            file_hash=file_hash,
            metadata=metadata
        )

        # Set previous_revision_id hanya jika ada
        if previous_id:
            rev_node.previous_revision_id = previous_id

        # Insert ke database
        db = mongodb.db
        try:
            result = await db.revisions.insert_one(rev_node.dict())
            rev_node.id = result.inserted_id
            logger.info(f"✅ Revision registered: {document_id} rev.{revision}")
        except Exception as e:
            logger.error(f"❌ Failed to insert revision: {e}")
            raise
        
        # Update cache
        if document_id not in self._graph_cache:
            self._graph_cache[document_id] = {}
        self._graph_cache[document_id][revision] = rev_node

        return rev_node
    
    async def _compute_changes(self, document_id: str, previous_id: Optional[ObjectId], 
                               new_parts: List[Dict]) -> List[PartChange]:
        """Compute changes between revisions"""
        if not previous_id:
            return []
        
        db = mongodb.db
        previous = await db.revisions.find_one({"_id": previous_id})
        if not previous:
            return []
        
        old_parts = {p["part_number"]: p for p in previous["parts"]}
        new_parts_map = {p["part_number"]: p for p in new_parts}
        
        changes = []
        
        # Added parts
        for pn in set(new_parts_map.keys()) - set(old_parts.keys()):
            changes.append(PartChange(
                part_number=pn,
                change_type=ChangeType.ADD,
                new_value=new_parts_map[pn]
            ))
        
        # Removed parts
        for pn in set(old_parts.keys()) - set(new_parts_map.keys()):
            changes.append(PartChange(
                part_number=pn,
                change_type=ChangeType.DELETE,
                old_value=old_parts[pn]
            ))
        
        # Modified parts
        for pn in set(old_parts.keys()) & set(new_parts_map.keys()):
            old = old_parts[pn]
            new = new_parts_map[pn]
            
            fields_changed = []
            if old.get("effectivity_values") != new.get("effectivity_values"):
                fields_changed.append("effectivity")
            if old.get("supplier_code") != new.get("supplier_code"):
                fields_changed.append("supplier_code")
            
            if fields_changed:
                changes.append(PartChange(
                    part_number=pn,
                    change_type=ChangeType.MODIFY,
                    old_value=old,
                    new_value=new,
                    fields_changed=fields_changed
                ))
        
        return changes
    
    async def get_revision_graph(self, document_id: str, force_rebuild: bool = False) -> Dict[str, RevisionNodeModel]:
        """Get revision graph for document (from cache or rebuild)"""
        
        if force_rebuild or document_id not in self._graph_cache:
            # Rebuild from database
            db = mongodb.db
            cursor = db.revisions.find({"document_id": document_id}).sort("created_at", 1)
            revisions = await cursor.to_list(length=None)
            
            graph = {}
            for rev_data in revisions:
                rev = RevisionNodeModel(**rev_data)
                graph[rev.revision] = rev
            
            self._graph_cache[document_id] = graph
            logger.info(f"🔄 Rebuilt graph for {document_id} with {len(graph)} revisions")
        
        return self._graph_cache.get(document_id, {})
    
    async def compare_revisions(self, document_id: str, rev_a: str, rev_b: str) -> Dict:
        """Compare two revisions"""
        graph = await self.get_revision_graph(document_id)
        
        if rev_a not in graph or rev_b not in graph:
            raise ValueError(f"Revision not found: {rev_a} or {rev_b}")
        
        node_a = graph[rev_a]
        node_b = graph[rev_b]
        
        return {
            "document_id": document_id,
            "from_revision": rev_a,
            "to_revision": rev_b,
            "changes": [c.dict() for c in node_b.changes],
            "summary": node_b.change_summary,
            "from_date": node_a.issue_date.isoformat() if node_a.issue_date else None,
            "to_date": node_b.issue_date.isoformat() if node_b.issue_date else None,
            "from_status": node_a.metadata.status.value,
            "to_status": node_b.metadata.status.value
        }
    
    async def get_part_lineage(self, part_number: str, document_id: str) -> List[Dict]:
        """Get evolution of a part across revisions"""
        graph = await self.get_revision_graph(document_id)
        
        # Sort revisions
        sorted_revs = sorted(graph.values(), key=lambda x: x.created_at)
        
        lineage = []
        for rev in sorted_revs:
            part = next((p for p in rev.parts if p.get("part_number") == part_number), None)
            
            lineage.append({
                "revision": rev.revision,
                "created_at": rev.created_at.isoformat(),
                "status": rev.metadata.status.value,
                "present": part is not None,
                "effectivity": part.get("effectivity_values") if part else None,
                "change_type": next(
                    (c.change_type.value for c in rev.changes if c.part_number == part_number),
                    None
                )
            })
        
        return lineage
    
    async def validate_consistency(self, document_id: str) -> List[str]:
        """Validate revision graph consistency"""
        graph = await self.get_revision_graph(document_id, force_rebuild=True)
        issues = []
        
        # Check for broken links
        db = mongodb.db
        for rev in graph.values():
            if rev.previous_revision_id:
                prev = await db.revisions.find_one({"_id": rev.previous_revision_id})
                if not prev:
                    issues.append(f"Broken link: {rev.revision} -> previous {rev.previous_revision_id}")
            
            if rev.next_revision_id:
                next_rev = await db.revisions.find_one({"_id": rev.next_revision_id})
                if not next_rev:
                    issues.append(f"Broken link: {rev.revision} -> next {rev.next_revision_id}")
        
        return issues
    
    async def clear_cache(self):
        """Clear in-memory cache (force rebuild on next access)"""
        self._graph_cache.clear()
        logger.info("🗑️ Authority cache cleared")
    
    async def _find_previous_revision(self, document_id: str, current_rev: str) -> Optional[ObjectId]:
        """Cari revisi sebelumnya berdasarkan numbering convention"""
        db = mongodb.db
        
        # Parse revision number (030.4 → 030.3)
        try:
            if '.' in current_rev:
                major, minor = current_rev.split('.')
                prev_minor = int(minor) - 1
                if prev_minor >= 0:
                    candidate = f"{major}.{prev_minor}"
                    
                    # Cari di cache dulu
                    if document_id in self._graph_cache and candidate in self._graph_cache[document_id]:
                        return self._graph_cache[document_id][candidate].id
                    
                    # Cari di database
                    prev = await db.revisions.find_one({
                        "document_id": document_id,
                        "revision": candidate
                    })
                    if prev:
                        return prev["_id"]
        except:
            pass
        
        # Fallback: ambil revision terakhir
        last = await db.revisions.find_one(
            {"document_id": document_id},
            sort=[("created_at", -1)]
        )
        if last:
            return last["_id"]
        
        return None

# Singleton
persistent_authority = PersistentAuthorityEngine()