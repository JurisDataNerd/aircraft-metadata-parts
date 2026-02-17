// 002_create_ipd_parts.js - UPDATE
db.createCollection("ipd_parts", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["ipd_part_id", "document_id", "part_number", "effectivity_type"],
      properties: {
        ipd_part_id: { bsonType: "string" },
        document_id: { bsonType: "string" }, // UBAH DARI objectId KE string!
        part_number: { bsonType: "string" },

        // Sticker-specific fields
        is_sticker: { bsonType: "bool" },
        sticker_type: {
          enum: ["PLACARD", "LABEL", "STENCIL", "DECAL", "MARKING"],
        },
        sticker_material: { bsonType: "string" },
        sticker_color: { bsonType: "string" },
        sticker_dimensions: {
          bsonType: ["object", "null"], // Allow null
          properties: {
            width: { bsonType: "double" },
            height: { bsonType: "double" },
            thickness: { bsonType: "double" },
          },
        },

        // Text content
        sticker_text: { bsonType: ["string", "null"] }, // Allow null
        font_specification: {
          bsonType: ["object", "null"], // Allow null
          properties: {
            font_family: { bsonType: "string" },
            font_size: { bsonType: "double" },
            font_style: { bsonType: "string" },
          },
        },

        // Original fields
        nomenclature: { bsonType: ["string", "null"] }, // Allow null
        figure: { bsonType: ["string", "null"] }, // Allow null
        item: { bsonType: ["string", "null"] }, // Allow null
        supplier_code: { bsonType: ["string", "null"] }, // Allow null
        effectivity_type: { enum: ["LIST", "RANGE"] },
        effectivity_values: {
          bsonType: ["array", "null"], // Allow null
          items: { bsonType: "int" },
        },
        effectivity_range: {
          bsonType: ["object", "null"], // Allow null
          properties: {
            from: { bsonType: "int" },
            to: { bsonType: "int" },
          },
        },
        upa: { bsonType: ["int", "null"] }, // Allow null
        sb_reference: { bsonType: ["string", "null"] }, // Allow null
        page_number: { bsonType: "int" },
        confidence: { bsonType: "double" },

        // Timestamps
        created_at: { bsonType: "date" },
      },
    },
  },
});

// Indexes
db.ipd_parts.createIndex({ ipd_part_id: 1 }, { unique: true });
db.ipd_parts.createIndex({ document_id: 1 });
db.ipd_parts.createIndex({ part_number: 1 });
db.ipd_parts.createIndex({ is_sticker: 1 });
db.ipd_parts.createIndex({ sticker_type: 1 });
db.ipd_parts.createIndex({ sticker_text: "text" });
db.ipd_parts.createIndex({ effectivity_type: 1, effectivity_values: 1 });
