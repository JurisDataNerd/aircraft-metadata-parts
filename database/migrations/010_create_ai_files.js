// Migration 010: AI Files for stickers
db.createCollection("ai_files", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["part_number", "file_path", "version"],
      properties: {
        part_number: { bsonType: "string" },
        revision: { bsonType: "string" },

        // File references
        file_path: { bsonType: "string" },
        preview_path: { bsonType: "string" },
        pdf_source: { bsonType: "string" },

        // File metadata
        file_size: { bsonType: "int" },
        file_hash: { bsonType: "string" },
        version: { bsonType: "int" },

        // Edit history
        edited_by: { bsonType: "string" },
        edited_at: { bsonType: "date" },
        edit_notes: { bsonType: "string" },

        // Export formats available
        formats_available: {
          bsonType: "object",
          properties: {
            ai: { bsonType: "bool" },
            pdf: { bsonType: "bool" },
            eps: { bsonType: "bool" },
            png: { bsonType: "bool" },
            svg: { bsonType: "bool" },
          },
        },

        created_at: { bsonType: "date" },
      },
    },
  },
});

// Indexes
db.ai_files.createIndex({ part_number: 1, version: -1 });
db.ai_files.createIndex({ file_hash: 1 });
