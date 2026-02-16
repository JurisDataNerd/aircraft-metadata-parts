// Part Master linking with sticker info
db.createCollection("part_master", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["part_number"],
      properties: {
        part_number: { bsonType: "string" },

        // Basic info
        is_sticker: { bsonType: "bool" },
        sticker_type: { bsonType: "string" },

        // References
        linked_ipd_parts: {
          bsonType: "array",
          items: { bsonType: "objectId" },
        },
        linked_drawing_items: {
          bsonType: "array",
          items: { bsonType: "objectId" },
        },

        // Latest AI file
        latest_ai_version: { bsonType: "int" },
        latest_ai_file_id: { bsonType: "objectId" },

        // Statistics
        total_revisions: { bsonType: "int" },
        first_appearance: { bsonType: "date" },
        last_modified: { bsonType: "date" },
      },
    },
  },
});

// Additional indexes
db.part_master.createIndex({ is_sticker: 1 });
db.part_master.createIndex({ sticker_type: 1 });
