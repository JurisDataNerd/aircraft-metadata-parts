// Drawing Items collection (FR-02)
db.createCollection("drawing_items", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["drawing_item_id", "document_id", "part_number"],
      properties: {
        drawing_item_id: { bsonType: "string" },
        document_id: { bsonType: "objectId" },
        part_number: { bsonType: "string" },
      },
    },
  },
});

db.drawing_items.createIndex({ part_number: 1 });
db.drawing_items.createIndex({ document_id: 1 });
