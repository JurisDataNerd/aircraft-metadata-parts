db.ipd_parts.createIndex({ part_number: 1 });
db.ipd_parts.createIndex({ effectivity_values: 1 });
db.ipd_parts.createIndex({ document_id: 1 });
db.ipd_parts.createIndex({ revision: 1 });
db.ipd_parts.createIndex({ part_number: 1, revision: 1 });

db.drawing_items.createIndex({ part_number: 1 });
db.drawing_items.createIndex({ document_id: 1 });

db.decision_log.createIndex({ user_id: 1, timestamp_open: -1 });
db.decision_log.createIndex({ part_number: 1, timestamp_open: -1 });
db.decision_log.createIndex({ line_number: 1, timestamp_open: -1 });

db.part_risk_profile.createIndex({ risk_score: -1 });
db.part_risk_profile.createIndex({ volatility_index: -1 });

db.config_drift_log.createIndex({ line_number: 1, detected_at: -1 });
db.config_drift_log.createIndex({ status: 1 });
