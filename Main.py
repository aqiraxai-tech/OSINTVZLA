import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

# --- CONFIGURACIÓN ---
APP_ID = "9237"
TOKEN_API = "3e0d7aad27f8a47e9bcebcee294671c7"
BOT_TOKEN = "MTQ4ODA0ODIxMTU1NjgyNzE4OA.GXRkuu.gCz8zWqqih05BXesbME2Ej4xjJ8sP1ClVL3XhM"
ROL_AUTORIZADO = "osint"
# ---------------------

class MiBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?", intents=discord.Intents.all())

    async def setup_hook(self):
        await self.tree.sync()

bot = MiBot()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(
        name="Aqirax",
        url="https://www.twitch.tv/xentury_oficial"
    ))
    print(f"✅ {bot.user.name} activo, menor.")

@bot.tree.command(name="cedula", description="Consulta datos CNE")
@app_commands.checks.has_role(ROL_AUTORIZADO)
async def cedula(interaction: discord.Interaction, nro: str):
    # Esto evita el error de "La aplicación no respondió"
    await interaction.response.defer()

    if not nro.isdigit():
        return await interaction.followup.send("🤡 Mano, pon solo los números.")

    url = f"https://api.cedula.com.ve/api/v1?app_id={APP_ID}&token={TOKEN_API}&nacionalidad=V&cedula={nro}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return await interaction.followup.send("💀 API caída, hay vale.")
                
                res = await response.json()
                if res.get("error"):
                    return await interaction.followup.send(f"⚠️ Error: {res.get('error_str', 'No encontrado.')}")

                d = res.get("data")
                c = d.get("cne", {})
                
                embed = discord.Embed(title=f"🔎 Registro CNE: {nro}", color=0x2b2d31)
                
                # Nombre
                nombre = f"{d.get('primer_nombre', '')} {d.get('segundo_nombre', '')} {d.get('primer_apellido', '')} {d.get('segundo_apellido', '')}"
                embed.add_field(name="👤 Nombre Completo", value=nombre.upper() or "N/A", inline=False)
                
                # Info extra
                embed.add_field(name="🆔 RIF", value=d.get('rif', 'N/A'), inline=True)
                embed.add_field(name="🌎 Nacionalidad", value=d.get('nacionalidad', 'V'), inline=True)
                
                # CNE
                embed.add_field(name="📍 Estado", value=c.get('estado', 'N/A'), inline=True)
                embed.add_field(name="🏙️ Municipio", value=c.get('municipio', 'N/A'), inline=True)
                embed.add_field(name="🗺️ Parroquia", value=c.get('parroquia', 'N/A'), inline=True)
                embed.add_field(name="🏛️ Centro Electoral", value=c.get('centro_electoral', 'No asignado'), inline=False)
                
                embed.set_footer(text=f"Consulta: {d.get('request_date', 'N/A')} | Aqirax OSINT")
                
                await interaction.followup.send(embed=embed)
                
    except Exception as e:
        print(f"🧨 Error técnico: {e}")
        await interaction.followup.send("🧨 Error técnico, revisa la consola.")

@cedula.error
async def cedula_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("🚫 Sapegato, necesitas el rol 'osint'.", ephemeral=True)

bot.run(BOT_TOKEN)
