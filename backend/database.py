from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure

from config import MONGODB_URI, MONGODB_DATABASE


# =========================================================
# MongoDB Connection
# =========================================================

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000,
)

try:
    client.admin.command("ping")
    print("MongoDB connected successfully.")
except ConnectionFailure as exc:
    raise RuntimeError(
        "Unable to connect to MongoDB."
    ) from exc


db = client[MONGODB_DATABASE]


# =========================================================
# Collections
# =========================================================

users = db["users"]
messages = db["messages"]
interactions = db["interactions"]
feedback = db["feedback"]
escalations = db["escalations"]
documents = db["documents"]
insights = db["insights"]
contributors = db["contributors"]
events = db["events"]
knowledge = db["knowledge"]
knowledge_candidates = db["knowledge_candidates"]

# =========================================================
# Indexes
# =========================================================

# -------------------------
# Users
# -------------------------

users.create_index(
    [("discord_id", ASCENDING)],
    unique=True,
)

users.create_index(
    [("joined_at", DESCENDING)]
)


# -------------------------
# Messages
# -------------------------

messages.create_index(
    [("discord_message_id", ASCENDING)],
    unique=True,
)

messages.create_index(
    [("user_id", ASCENDING), ("created_at", DESCENDING)]
)

messages.create_index(
    [("created_at", DESCENDING)]
)

messages.create_index(
    [("topic", ASCENDING), ("created_at", DESCENDING)]
)

messages.create_index(
    [("intent", ASCENDING), ("created_at", DESCENDING)]
)

messages.create_index(
    [("resolved", ASCENDING)]
)

messages.create_index(
    [("escalated", ASCENDING)]
)


# -------------------------
# Interactions
# -------------------------

interactions.create_index(
    [("message_id", ASCENDING)]
)

interactions.create_index(
    [("user_id", ASCENDING), ("created_at", DESCENDING)]
)

interactions.create_index(
    [("type", ASCENDING), ("created_at", DESCENDING)]
)

interactions.create_index(
    [("topic", ASCENDING), ("created_at", DESCENDING)]
)

interactions.create_index(
    [("created_at", DESCENDING)]
)


# -------------------------
# Feedback
# -------------------------

feedback.create_index(
    [("created_at", DESCENDING)]
)

feedback.create_index(
    [("topic", ASCENDING)]
)

feedback.create_index(
    [("status", ASCENDING)]
)


# -------------------------
# Escalations
# -------------------------

escalations.create_index(
    [("created_at", DESCENDING)]
)

escalations.create_index(
    [("topic", ASCENDING)]
)

escalations.create_index(
    [("priority", ASCENDING)]
)


# -------------------------
# Documents
# -------------------------

documents.create_index(
    [("created_at", DESCENDING)]
)

documents.create_index(
    [("status", ASCENDING)]
)


# -------------------------
# Knowledge
# -------------------------

knowledge.create_index(
    [
        ("topic", ASCENDING),
        ("category", ASCENDING),
    ]
)

knowledge.create_index(
    [("tags", ASCENDING)]
)

knowledge.create_index(
    [
        ("title", "text"),
        ("content", "text"),
        ("tags", "text"),
    ]
)


# -------------------------
# Events
# -------------------------

events.create_index(
    [("date", ASCENDING)]
)


# -------------------------
# Contributors
# -------------------------

# -------------------------
# Contributors
# -------------------------

contributors.create_index(
    [("discord_id", ASCENDING)],
    unique=True,
)

contributors.create_index(
    [("message_count", DESCENDING)]
)

contributors.create_index(
    [("last_active", DESCENDING)]
)

contributors.create_index(
    [("impact_score", DESCENDING)]
)


# -------------------------
# Events
# -------------------------

events.create_index(
    [("created_at", DESCENDING)]
)

events.create_index(
    [("user_id", ASCENDING), ("created_at", DESCENDING)]
)

events.create_index(
    [("type", ASCENDING), ("created_at", DESCENDING)]
)

events.create_index(
    [("channel", ASCENDING), ("created_at", DESCENDING)]
)

print("MongoDB collections and indexes ready.")