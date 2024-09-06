class Persona:
    def __init__(self, name: str, avatar: str, voice: str):
        self.name = name
        self.avatar = avatar
        self.voice = voice

    def __repr__(self) -> str:
        return f"<Persona: {self.name}>"


def generate_personas():
    presets = [
        {
            "name": "Alice",
            "avatar": "alice.jpeg",
            "voice": "en-US-Journey-O",
        },
        {
            "name": "John",
            "avatar": "john.jpeg",
            "voice": "en-US-Journey-D",
        },
        {
            "name": "Sophia",
            "avatar": "sophia.jpeg",
            "voice": "en-US-Journey-F",
        },
    ]

    personas = {}
    for i in presets:
        name = i["name"]
        avatar = i["avatar"]
        voice = i["voice"]
        persona = Persona(name, avatar, voice)
        personas[name] = persona
    return personas


personas = generate_personas()
