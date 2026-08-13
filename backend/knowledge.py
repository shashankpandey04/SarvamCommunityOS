from database import db


knowledge = db["knowledge"]


def add_knowledge(
    title: str,
    topic: str,
    category: str,
    content: str,
    tags: list[str] | None = None,
    source: str = "official",
):
    """
    Add an official knowledge entry to CommunityOS.
    """

    document = {
        "title": title,
        "topic": topic,
        "category": category,
        "content": content.strip(),
        "tags": tags or [],
        "source": source,
    }

    result = knowledge.insert_one(document)

    return str(result.inserted_id)


def search_knowledge(
    topic: str | None = None,
    keywords: list[str] | None = None,
    limit: int = 5,
):
    """
    Search CommunityOS knowledge.

    Topic is the primary filter.
    Keywords rank entries within that topic.
    """

    query = {}

    if topic:
        query["topic"] = {
            "$regex": f"^{topic}$",
            "$options": "i",
        }

    results = list(
        knowledge.find(
            query,
            {
                "_id": 0,
                "title": 1,
                "topic": 1,
                "category": 1,
                "content": 1,
                "tags": 1,
                "source": 1,
            },
        )
    )

    # If a topic was supplied but nothing matched,
    # don't return unrelated knowledge.
    if topic and not results:
        return []

    if not keywords:
        return results[:limit]

    # Score results within the selected topic.
    scored = []

    for item in results:
        title = item.get("title", "").lower()
        content = item.get("content", "").lower()
        tags = [
            tag.lower()
            for tag in item.get("tags", [])
        ]

        score = 0

        for keyword in keywords:
            keyword = keyword.lower().strip()

            if keyword in title:
                score += 3

            if keyword in tags:
                score += 3

            if keyword in content:
                score += 1

        if score > 0:
            scored.append((score, item))

    scored.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        item
        for _, item in scored[:limit]
    ]

def build_context(results: list[dict]) -> str:
    """
    Convert retrieved knowledge into context
    that can be provided to Sarvam 105B.
    """

    if not results:
        return "No relevant community knowledge was found."

    sections = []

    for index, item in enumerate(results, start=1):

        sections.append(
            f"""
Knowledge {index}

Title: {item.get("title", "")}
Topic: {item.get("topic", "")}
Category: {item.get("category", "")}
Source: {item.get("source", "")}

Content:
{item.get("content", "")}
""".strip()
        )

    return "\n\n---\n\n".join(sections)