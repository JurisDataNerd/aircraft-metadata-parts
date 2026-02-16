// ============== IPD PARTS INDEXES ==============
// Basic indexes
db.ipd_parts.createIndex({ part_number: 1 });
db.ipd_parts.createIndex({ document_id: 1 });
db.ipd_parts.createIndex({ revision: 1 });
db.ipd_parts.createIndex({ part_number: 1, revision: 1 });

// Effectivity indexes
db.ipd_parts.createIndex({ effectivity_values: 1 });
db.ipd_parts.createIndex({ "effectivity_range.from": 1, "effectivity_range.to": 1 });

// Sticker-specific indexes (NEW)
db.ipd_parts.createIndex({ is_sticker: 1 });
db.ipd_parts.createIndex({ sticker_type: 1 });
db.ipd_parts.createIndex({ sticker_material: 1 });
db.ipd_parts.createIndex({ sticker_color: 1 });

// Text search for sticker content (NEW)
db.ipd_parts.createIndex({ sticker_text: "text" });
db.ipd_parts.createIndex({ nomenclature: "text" });

// Composite indexes for common queries (NEW)
db.ipd_parts.createIndex({ is_sticker: 1, sticker_type: 1 });
db.ipd_parts.createIndex({ is_sticker: 1, part_number: 1 });
db.ipd_parts.createIndex({ sticker_type: 1, effectivity_values: 1 });

// ============== DRAWING ITEMS INDEXES ==============
db.drawing_items.createIndex({ part_number: 1 });
db.drawing_items.createIndex({ document_id: 1 });
db.drawing_items.createIndex({ item_number: 1 });

// ============== PART MASTER INDEXES (UPDATED) ==============
db.part_master.createIndex({ part_number: 1 }, { unique: true });
db.part_master.createIndex({ is_sticker: 1 }); // NEW
db.part_master.createIndex({ sticker_type: 1 }); // NEW
db.part_master.createIndex({ latest_ai_version: -1 }); // NEW

// ============== REVISIONS INDEXES (UPDATED) ==============
db.revisions.createIndex({ document_id: 1, revision: 1 }, { unique: true });
db.revisions.createIndex({ document_id: 1, created_at: -1 });
db.revisions.createIndex({ previous_revision_id: 1 });
db.revisions.createIndex({ next_revision_id: 1 });
db.revisions.createIndex({ "metadata.status": 1 });
db.revisions.createIndex({ file_hash: 1 });
db.revisions.createIndex({ "parts.is_sticker": 1 }); // NEW
db.revisions.createIndex({ sticker_count: 1 }); // NEW
db.revisions.createIndex({ "parts.part_number": 1 }); // NEW

// ============== STICKER TEMPLATES INDEXES (NEW) ==============
db.sticker_templates.createIndex({ template_name: 1 }, { unique: true });
db.sticker_templates.createIndex({ template_type: 1 });
db.sticker_templates.createIndex({ aircraft_models: 1 });
db.sticker_templates.createIndex({ created_by: 1 });
db.sticker_templates.createIndex({ template_type: 1, aircraft_models: 1 });

// ============== AI FILES INDEXES (NEW) ==============
db.ai_files.createIndex({ part_number: 1, version: -1 });
db.ai_files.createIndex({ part_number: 1, revision: 1 });
db.ai_files.createIndex({ file_hash: 1 }, { unique: true });
db.ai_files.createIndex({ edited_by: 1, edited_at: -1 });
db.ai_files.createIndex({ "formats_available.ai": 1 }); // Find stickers with AI files
db.ai_files.createIndex({ part_number: 1, "formats_available.png": 1 });

// ============== DECISION LOG INDEXES ==============
db.decision_log.createIndex({ user_id: 1, timestamp_open: -1 });
db.decision_log.createIndex({ part_number: 1, timestamp_open: -1 });
db.decision_log.createIndex({ line_number: 1, timestamp_open: -1 });
db.decision_log.createIndex({ decision: 1 }); // NEW
db.decision_log.createIndex({ part_number: 1, line_number: 1 }); // NEW

// ============== PART RISK PROFILE INDEXES ==============
db.part_risk_profile.createIndex({ risk_score: -1 });
db.part_risk_profile.createIndex({ volatility_index: -1 });
db.part_risk_profile.createIndex({ part_number: 1 }, { unique: true }); // NEW
db.part_risk_profile.createIndex({ last_reviewed: -1 }); // NEW

// ============== CONFIG DRIFT LOG INDEXES ==============
db.config_drift_log.createIndex({ line_number: 1, detected_at: -1 });
db.config_drift_log.createIndex({ status: 1 });
db.config_drift_log.createIndex({ resolved_at: 1 }); // NEW
db.config_drift_log.createIndex({ detected_by: 1 }); // NEW

// ============== DOCUMENTS INDEXES (UPDATED) ==============
db.documents.createIndex({ document_number: 1, revision: 1 }, { unique: true });
db.documents.createIndex({ document_type: 1 });
db.documents.createIndex({ aircraft_model: 1 });
db.documents.createIndex({ issue_date: -1 });
db.documents.createIndex({ file_hash: 1 }); // NEW

// ============== AUDIT LOGS INDEXES ==============
db.audit_logs.createIndex({ document_id: 1, timestamp: -1 });
db.audit_logs.createIndex({ user_id: 1, timestamp: -1 });
db.audit_logs.createIndex({ action: 1, timestamp: -1 });
db.audit_logs.createIndex({ part_number: 1, timestamp: -1 }); // NEW

print("✅ All indexes created successfully!");
