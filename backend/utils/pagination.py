import discord


MAX_PAGE_LENGTH = 1500


def paginate_text(
    text: str,
    max_length: int = MAX_PAGE_LENGTH,
) -> list[str]:

    if len(text) <= max_length:
        return [text]

    pages = []

    while len(text) > max_length:

        split_at = text.rfind(
            "\n",
            0,
            max_length,
        )

        if split_at == -1:
            split_at = text.rfind(
                " ",
                0,
                max_length,
            )

        if split_at == -1:
            split_at = max_length

        pages.append(
            text[:split_at].strip()
        )

        text = text[split_at:].strip()

    if text:
        pages.append(text)

    return pages

class AnswerPaginator(discord.ui.View):

    def __init__(
        self,
        pages: list[str],
        user_id: int,
    ):
        super().__init__(timeout=300)

        self.pages = pages
        self.user_id = user_id
        self.current_page = 0

        self.previous_button.disabled = True

        if len(self.pages) <= 1:
            self.next_button.disabled = True

    async def interaction_check(
        self,
        interaction: discord.Interaction,
    ) -> bool:

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "❌ You cannot control this pagination.",
                ephemeral=True,
            )

            return False

        return True

    def update_buttons(self):

        self.previous_button.disabled = (
            self.current_page == 0
        )

        self.next_button.disabled = (
            self.current_page >= len(self.pages) - 1
        )

    @discord.ui.button(
        label="Previous",
        emoji="◀️",
        style=discord.ButtonStyle.secondary,
    )
    async def previous_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):

        self.current_page -= 1

        self.update_buttons()

        await interaction.response.edit_message(
            content=self.pages[self.current_page],
            view=self,
        )

    @discord.ui.button(
        label="Next",
        emoji="▶️",
        style=discord.ButtonStyle.primary,
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):

        self.current_page += 1

        self.update_buttons()

        await interaction.response.edit_message(
            content=self.pages[self.current_page],
            view=self,
        )