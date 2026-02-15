from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class RevisionNode:
    """Representasi satu revisi dokumen"""
    
    def __init__(self, 
                 document_id: str,
                 revision: str,
                 issue_date: datetime,
                 parts: List[Dict],
                 change_summary: Dict,
                 previous_revision: Optional['RevisionNode'] = None):
        
        self.document_id = document_id
        self.revision = revision
        self.issue_date = issue_date
        self.parts = {p["part_number"]: p for p in parts}  # Map by part number
        self.change_summary = change_summary
        self.previous = previous_revision
        self.next = None
        self.branch = "main"
        self.approval_status = "approved"
        self.created_at = datetime.utcnow()
        
    def compute_delta(self, other: 'RevisionNode') -> Dict:
        """Hitung perubahan antara dua revisi"""
        added = set(other.parts.keys()) - set(self.parts.keys())
        removed = set(self.parts.keys()) - set(other.parts.keys())
        
        # Modified parts
        modified = []
        for pn in set(self.parts.keys()) & set(other.parts.keys()):
            p1 = self.parts[pn]
            p2 = other.parts[pn]
            
            changes = {}
            if p1.get("effectivity_values") != p2.get("effectivity_values"):
                changes["effectivity"] = {
                    "old": p1.get("effectivity_values"),
                    "new": p2.get("effectivity_values")
                }
            if p1.get("supplier_code") != p2.get("supplier_code"):
                changes["supplier_code"] = {
                    "old": p1.get("supplier_code"),
                    "new": p2.get("supplier_code")
                }
            if p1.get("nomenclature") != p2.get("nomenclature"):
                changes["nomenclature"] = {
                    "old": p1.get("nomenclature"),
                    "new": p2.get("nomenclature")
                }
            
            if changes:
                modified.append({
                    "part_number": pn,
                    "changes": changes
                })
        
        return {
            "from_rev": self.revision,
            "to_rev": other.revision,
            "added_parts": list(added),
            "removed_parts": list(removed),
            "modified_parts": modified,
            "timestamp": datetime.utcnow().isoformat()
        }


class RevisionGraph:
    """Menyimpan seluruh riwayat revisi sebagai DAG"""
    
    def __init__(self, document_id: str):
        self.document_id = document_id
        self.nodes: Dict[str, RevisionNode] = {}
        self.head: Optional[RevisionNode] = None
        
    def add_revision(self, 
                     revision: str,
                     issue_date: datetime,
                     parts: List[Dict],
                     change_summary: Dict,
                     previous_rev: Optional[str] = None) -> RevisionNode:
        """Tambah revisi baru"""
        
        previous_node = self.nodes.get(previous_rev) if previous_rev else self.head
        
        node = RevisionNode(
            document_id=self.document_id,
            revision=revision,
            issue_date=issue_date,
            parts=parts,
            change_summary=change_summary,
            previous_revision=previous_node
        )
        
        if previous_node:
            previous_node.next = node
        
        self.nodes[revision] = node
        
        if not self.head or (previous_rev and previous_rev in self.nodes):
            self.head = node
        
        return node
    
    def get_timeline(self) -> List[Dict]:
        """Dapatkan timeline revisi"""
        if not self.head:
            return []
        
        # Cari root
        current = self.head
        while current.previous:
            current = current.previous
        
        timeline = []
        while current:
            timeline.append({
                "revision": current.revision,
                "issue_date": current.issue_date.isoformat(),
                "change_summary": current.change_summary,
                "total_parts": len(current.parts),
                "has_next": current.next is not None
            })
            current = current.next
        
        return timeline
    
    def compare_revisions(self, rev_a: str, rev_b: str) -> Dict:
        """Bandingkan dua revisi"""
        if rev_a not in self.nodes or rev_b not in self.nodes:
            raise ValueError(f"Revision not found: {rev_a} or {rev_b}")
        
        return self.nodes[rev_a].compute_delta(self.nodes[rev_b])
    
    def get_part_evolution(self, part_number: str) -> List[Dict]:
        """Lihat evolusi suatu part"""
        evolution = []
        timeline = self.get_timeline()
        
        for rev_info in timeline:
            rev = self.nodes[rev_info["revision"]]
            part = rev.parts.get(part_number)
            
            evolution.append({
                "revision": rev.revision,
                "issue_date": rev.issue_date.isoformat(),
                "present": part is not None,
                "effectivity": part.get("effectivity_values") if part else None,
                "change_type": part.get("change_type") if part else None,
                "supplier_code": part.get("supplier_code") if part else None
            })
        
        return evolution


class AuthorityEngine:
    """Authority engine dengan revision intelligence"""
    
    def __init__(self):
        self.revision_graphs: Dict[str, RevisionGraph] = {}
        self.validation_rules = []
        
    def register_document(self, doc_data: Dict, parts: List[Dict]) -> RevisionNode:
        """Daftarkan dokumen baru"""
        doc_id = doc_data["document_id"]
        revision = doc_data["revision"]
        
        # Buat atau ambil graph
        if doc_id not in self.revision_graphs:
            self.revision_graphs[doc_id] = RevisionGraph(doc_id)
        
        graph = self.revision_graphs[doc_id]
        
        # Cari previous revision
        previous_rev = self._find_previous_revision(doc_id, revision)
        
        # Hitung change summary
        change_summary = self._compute_change_summary(
            graph.nodes.get(previous_rev) if previous_rev else None,
            parts
        )
        
        # Tambah ke graph
        node = graph.add_revision(
            revision=revision,
            issue_date=doc_data.get("issue_date", datetime.utcnow()),
            parts=parts,
            change_summary=change_summary,
            previous_rev=previous_rev
        )
        
        # Validasi konsistensi
        self._validate_revision_consistency(node)
        
        return node
    
    def _find_previous_revision(self, doc_id: str, current_rev: str) -> Optional[str]:
        """Cari revisi sebelumnya"""
        graph = self.revision_graphs.get(doc_id)
        if not graph:
            return None
        
        # Parse revision number (030.4 → 030.3)
        if '.' in current_rev:
            try:
                major, minor = current_rev.split('.')
                prev_minor = int(minor) - 1
                if prev_minor >= 0:
                    candidate = f"{major}.{prev_minor}"
                    if candidate in graph.nodes:
                        return candidate
            except:
                pass
        
        # Fallback: ambil yang terakhir
        timeline = graph.get_timeline()
        if timeline:
            return timeline[-1]["revision"]
        
        return None
    
    def _compute_change_summary(self, previous_node: Optional[RevisionNode], 
                                new_parts: List[Dict]) -> Dict:
        """Hitung ringkasan perubahan"""
        if not previous_node:
            return {
                "type": "INITIAL",
                "total_parts": len(new_parts)
            }
        
        old_parts = {p["part_number"]: p for p in previous_node.parts.values()}
        new_parts_map = {p["part_number"]: p for p in new_parts}
        
        added = set(new_parts_map.keys()) - set(old_parts.keys())
        removed = set(old_parts.keys()) - set(new_parts_map.keys())
        
        # Modified parts
        modified = []
        for pn in set(old_parts.keys()) & set(new_parts_map.keys()):
            old = old_parts[pn]
            new = new_parts_map[pn]
            
            changes = {}
            if old.get("effectivity_values") != new.get("effectivity_values"):
                changes["effectivity"] = {
                    "old": old.get("effectivity_values"),
                    "new": new.get("effectivity_values")
                }
            
            if changes:
                modified.append({
                    "part_number": pn,
                    "changes": changes
                })
        
        return {
            "type": "UPDATE",
            "added_parts": list(added),
            "removed_parts": list(removed),
            "modified_parts": modified,
            "total_parts": len(new_parts)
        }
    
    def _validate_revision_consistency(self, node: RevisionNode):
        """Validasi konsistensi antar revisi"""
        if not node.previous:
            return
        
        # Rule 1: Part yang di DELETE tidak boleh muncul lagi
        prev_changes = node.previous.change_summary
        if "removed_parts" in prev_changes:
            for removed in prev_changes["removed_parts"]:
                if removed in node.parts:
                    logger.warning(f"⚠️ Part {removed} muncul lagi setelah DELETE")
        
        # Rule 2: ADD tidak boleh untuk part yang sudah ada
        if "added_parts" in node.change_summary:
            for added in node.change_summary["added_parts"]:
                if added in node.previous.parts:
                    logger.warning(f"⚠️ Part {added} di-ADD tapi sudah ada sebelumnya")
    
    def get_audit_trail(self, document_id: str) -> Dict:
        """Dapatkan audit trail lengkap"""
        graph = self.revision_graphs.get(document_id)
        if not graph:
            return {"error": "Document not found"}
        
        timeline = graph.get_timeline()
        
        # Hitung delta antar revisi
        deltas = []
        for i in range(len(timeline) - 1):
            rev_a = timeline[i]["revision"]
            rev_b = timeline[i + 1]["revision"]
            deltas.append(graph.compare_revisions(rev_a, rev_b))
        
        return {
            "document_id": document_id,
            "revision_history": timeline,
            "changes": deltas,
            "total_revisions": len(timeline)
        }
    
    def validate_part_lineage(self, part_number: str, document_id: str) -> Dict:
        """Validasi lineage suatu part"""
        graph = self.revision_graphs.get(document_id)
        if not graph:
            return {"error": "Document not found"}
        
        evolution = graph.get_part_evolution(part_number)
        
        # Deteksi anomali
        anomalies = []
        for i in range(len(evolution) - 1):
            curr = evolution[i]
            nxt = evolution[i + 1]
            
            if curr["present"] and not nxt["present"]:
                anomalies.append(f"Part menghilang di rev {nxt['revision']}")
            elif not curr["present"] and nxt["present"] and nxt.get("change_type") != "ADD":
                anomalies.append(f"Part muncul tanpa ADD di rev {nxt['revision']}")
        
        return {
            "part_number": part_number,
            "document_id": document_id,
            "evolution": evolution,
            "anomalies": anomalies,
            "is_consistent": len(anomalies) == 0
        }


# Singleton instance
authority_engine = AuthorityEngine()