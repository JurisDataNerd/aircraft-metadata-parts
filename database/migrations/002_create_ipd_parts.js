// Migration 002: IPD Parts collection (UPDATED FOR STICKERS)
db.createCollection("ipd_parts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["ipd_part_id", "document_id", "part_number", "effectivity_type"],
      properties: {
        ipd_part_id: { bsonType: "string" },
        document_id: { bsonType: "objectId" },
        part_number: { bsonType: "string" },

        // Sticker-specific fields
        is_sticker: { bsonType: "bool" },
        sticker_type: {
          enum: ["PLACARD", "LABEL", "STENCIL", "DECAL", "MARKING"],
        },
        sticker_material: { bsonType: "string" }, // VINYL, POLYESTER, etc
        sticker_color: { bsonType: "string" }, // PMS or RGB
        sticker_dimensions: {
          bsonType: "object",
          properties: {
            width: { bsonType: "double" },
            height: { bsonType: "double" },
            thickness: { bsonType: "double" },
          },
        },

        // Text content
        sticker_text: { bsonType: "string" }, // The actual text on sticker
        font_specification: {
          bsonType: "object",
          properties: {
            font_family: { bsonType: "string" },
            font_size: { bsonType: "double" },
            font_style: { bsonType: "string" }, // BOLD, ITALIC, etc
          },
        },

        // Original fields
        nomenclature: { bsonType: "string" },
        figure: { bsonType: "string" },
        item: { bsonType: "string" },
        supplier_code: { bsonType: "string" },
        effectivity_type: { enum: ["LIST", "RANGE"] },
        effectivity_values: { bsonType: "array" },
        effectivity_range: {
          bsonType: "object",
          properties: {
            from: { bsonType: "int" },
            to: { bsonType: "int" },
          },
        },
        upa: { bsonType: "int" },
        sb_reference: { bsonType: "string" },
        page_number: { bsonType: "int" },
        confidence: { bsonType: "double" },
      },
    },
  },
});

// Additional indexes
db.ipd_parts.createIndex({ is_sticker: 1 });
db.ipd_parts.createIndex({ sticker_type: 1 });
db.ipd_parts.createIndex({ sticker_text: "text" }); // For text search
