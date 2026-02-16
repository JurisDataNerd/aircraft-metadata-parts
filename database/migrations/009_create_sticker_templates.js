// Migration 009: Sticker Templates
db.createCollection("sticker_templates", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["template_name", "template_type", "default_dimensions"],
      properties: {
        template_name: { bsonType: "string" },
        template_type: {
          enum: ["NO_STEP", "CAUTION", "WARNING", "DANGER", "INFO", "SERIAL"],
        },

        // Default specifications
        default_dimensions: {
          bsonType: "object",
          properties: {
            width: { bsonType: "double" },
            height: { bsonType: "double" },
          },
        },
        default_material: { bsonType: "string" },
        default_color: { bsonType: "string" },

        // Default text elements
        default_text_elements: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              text: { bsonType: "string" },
              font_family: { bsonType: "string" },
              font_size: { bsonType: "double" },
              font_style: { bsonType: "string" },
              x_position: { bsonType: "double" },
              y_position: { bsonType: "double" },
              width: { bsonType: "double" },
              height: { bsonType: "double" },
              color: { bsonType: "string" },
              alignment: { bsonType: "string" },
            },
          },
        },

        // Variables that can be customized
        variables: {
          bsonType: "array",
          items: { bsonType: "string" },
        },

        // Metadata
        aircraft_models: {
          bsonType: "array",
          items: { bsonType: "string" },
        },
        created_at: { bsonType: "date" },
        created_by: { bsonType: "string" },
      },
    },
  },
});

// Indexes
db.sticker_templates.createIndex({ template_name: 1 }, { unique: true });
db.sticker_templates.createIndex({ template_type: 1 });
