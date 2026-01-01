import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View, Modal, TextInput
import json
import os
from datetime import datetime, timedelta
import asyncio
import random
from keep_alive import keep_alive

# ===== BOT SETUP =====
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# ===== KONFIGURATION =====
# WICHTIG: Trage hier deine IDs ein!
OWNER_ID = 0  # DEINE Discord User-ID hier eintragen!
WILLKOMMEN_CHANNEL_ID = 0  # ID vom Willkommens-Channel
REGELN_CHANNEL_ID = 0  # ID vom Regeln-Channel
ROLLEN_CHANNEL_ID = 0  # ID vom Rollen-Channel
TICKET_CHANNEL_ID = 0  # ID vom Ticket-Channel
TICKET_CATEGORY_ID = 0  # ID der Ticket-Kategorie
MOD_ROLE_ID = 0  # ID der Moderator-Rolle
SUPPORT_ROLE_ID = 0  # ID der Support-Rolle (optional)
LOG_CHANNEL_ID = 0  # ID für Mod-Logs (optional)
AUTO_REPORT_CHANNEL_ID = 0  # ID für Auto-Reports (WICHTIG!)
CREATE_VOICE_CHANNEL_ID = 0  # ID vom "Erstelle deinen Channel"
VOICE_CATEGORY_ID = 0  # ID der Voice-Kategorie

# ===== BLACKLIST WÖRTER =====
# Extreme Wörter (INSTANT BAN + Nachricht löschen)
EXTREME_WORDS = [
    "hitler", "nazi", "hakenkreuz", "swastika", "holocaust", "heil",
    "drittes reich", "führer", "neger", "nigger", "kanake", 
    "judensau", "schlitzauge", "reichsbürger"
]

# Normale Blacklist (Report + Nachricht löschen)
BLACKLIST_WORDS = [
    # Füge hier die extremen Wörter hinzu
    "hitler", "nazi", "hakenkreuz", "swastika", "holocaust", "heil", 
    "drittes reich", "führer", "reichsbürger", "afd", "npd",
    "neger", "nigger", "kanake", "judensau", "schlitzauge",
    
    # Schwere Beleidigungen
    "hurensohn", "fotze", "wichser", "missgeburt", "bastard",
    "arschloch", "schlampe", "nutte", "bitch", "hure",
    
    # Sexuelle Inhalte
    "porn", "sex", "fick", "bumsen", "xxx", "porno",
    
    # Drogen
    "kokain", "heroin", "crystal", "meth",
]

# ===== DATENBANKEN =====
if not os.path.exists('levels.json'):
    with open('levels.json', 'w') as f:
        json.dump({}, f)

if not os.path.exists('tickets.json'):
    with open('tickets.json', 'w') as f:
        json.dump({'counter': 0}, f)

if not os.path.exists('giveaways.json'):
    with open('giveaways.json', 'w') as f:
        json.dump({}, f)

if not os.path.exists('warnings.json'):
    with open('warnings.json', 'w') as f:
        json.dump({}, f)

if not os.path.exists('reports.json'):
    with open('reports.json', 'w') as f:
        json.dump({}, f)

if not os.path.exists('voice_channels.json'):
    with open('voice_channels.json', 'w') as f:
        json.dump({}, f)

if not os.path.exists('reaction_roles.json'):
    with open('reaction_roles.json', 'w') as f:
        json.dump({}, f)

def load_levels():
    with open('levels.json', 'r') as f:
        return json.load(f)

def save_levels(data):
    with open('levels.json', 'w') as f:
        json.dump(data, f, indent=4)

def load_tickets():
    with open('tickets.json', 'r') as f:
        return json.load(f)

def save_tickets(data):
    with open('tickets.json', 'w') as f:
        json.dump(data, f, indent=4)

def load_giveaways():
    with open('giveaways.json', 'r') as f:
        return json.load(f)

def save_giveaways(data):
    with open('giveaways.json', 'w') as f:
        json.dump(data, f, indent=4)

def load_warnings():
    with open('warnings.json', 'r') as f:
        return json.load(f)

def save_warnings(data):
    with open('warnings.json', 'w') as f:
        json.dump(data, f, indent=4)

def load_reports():
    with open('reports.json', 'r') as f:
        return json.load(f)

def save_reports(data):
    with open('reports.json', 'w') as f:
        json.dump(data, f, indent=4)

def load_voice_channels():
    with open('voice_channels.json', 'r') as f:
        return json.load(f)

def save_voice_channels(data):
    with open('voice_channels.json', 'w') as f:
        json.dump(data, f, indent=4)

def load_reaction_roles():
    with open('reaction_roles.json', 'r') as f:
        return json.load(f)

def save_reaction_roles(data):
    with open('reaction_roles.json', 'w') as f:
        json.dump(data, f, indent=4)

# ===== BOT READY & SYNC =====
@bot.event
async def on_ready():
    print('='*50)
    print(f'✅ {bot.user} ist online!')
    print(f'📊 Verbunden mit {len(bot.guilds)} Server(n)')
    print('='*50)
    
    # Slash Commands synchronisieren
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} Slash-Commands synchronisiert!')
    except Exception as e:
        print(f'❌ Fehler beim Synchronisieren: {e}')
    
    # Status ändern
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.streaming,
            name="🐼 Panda's Karten Paradies",
            url="https://twitch.tv/pandapalette"
        )
    )
    
    # Starte Tasks
    check_giveaways.start()
    print('🎁 Giveaway-System gestartet!')
    print('🛡️ Auto-Moderation aktiv!')
    print('🎤 Auto Voice Channels aktiviert!')
    print('🎭 Reaction Roles System aktiv!')
    print('='*50)

# ===== WILLKOMMENSNACHRICHT =====
@bot.event
async def on_member_join(member):
    if WILLKOMMEN_CHANNEL_ID == 0:
        return
    
    welcome_channel = bot.get_channel(WILLKOMMEN_CHANNEL_ID)
    if welcome_channel:
        embed = discord.Embed(
            title="🐼 Willkommen im Paradies!",
            description=f"Hey {member.mention}! Schön, dass du da bist!\n\n"
                       f"**Los geht's:**\n"
                       f"📜 Lies dir die <#{REGELN_CHANNEL_ID}> durch\n"
                       f"🎭 Hole dir deine <#{ROLLEN_CHANNEL_ID}>\n"
                       f"💬 Chatte mit der Community!\n"
                       f"🔴 Verpasse keine Streams!\n\n"
                       f"Viel Spaß! 🎨⛏️",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Mitglied #{member.guild.member_count}")
        await welcome_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    if LOG_CHANNEL_ID == 0:
        return
    
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="👋 Mitglied verlassen",
            description=f"{member.mention} ({member.name}) hat den Server verlassen.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await log_channel.send(embed=embed)

# ===== AUTO VOICE CHANNELS =====
@bot.event
async def on_voice_state_update(member, before, after):
    """Erstellt und löscht automatisch Voice Channels"""
    
    if CREATE_VOICE_CHANNEL_ID == 0 or VOICE_CATEGORY_ID == 0:
        return
    
    voice_channels = load_voice_channels()
    
    # User joined the "Create Channel" voice
    if after.channel and after.channel.id == CREATE_VOICE_CHANNEL_ID:
        category = bot.get_channel(VOICE_CATEGORY_ID)
        
        if category:
            channel_name = f"🎮 {member.display_name}'s Channel"
            
            new_channel = await category.create_voice_channel(
                name=channel_name,
                user_limit=10
            )
            
            await member.move_to(new_channel)
            
            voice_channels[str(new_channel.id)] = {
                'owner': member.id,
                'created_at': datetime.utcnow().isoformat()
            }
            save_voice_channels(voice_channels)
            
            if LOG_CHANNEL_ID != 0:
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    embed = discord.Embed(
                        title="🎤 Voice Channel erstellt",
                        description=f"{member.mention} hat einen Voice Channel erstellt: **{channel_name}**",
                        color=discord.Color.green(),
                        timestamp=datetime.utcnow()
                    )
                    await log_channel.send(embed=embed)
    
    # User left a temporary channel
    if before.channel:
        channel_id = str(before.channel.id)
        
        if channel_id in voice_channels:
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                    del voice_channels[channel_id]
                    save_voice_channels(voice_channels)
                    
                    if LOG_CHANNEL_ID != 0:
                        log_channel = bot.get_channel(LOG_CHANNEL_ID)
                        if log_channel:
                            embed = discord.Embed(
                                title="🗑️ Voice Channel gelöscht",
                                description=f"Temporärer Channel wurde automatisch gelöscht (leer).",
                                color=discord.Color.red(),
                                timestamp=datetime.utcnow()
                            )
                            await log_channel.send(embed=embed)
                except:
                    pass

# ===== AUTO-MODERATION + LEVEL SYSTEM =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # AUTO-MODERATION
    if not message.author.guild_permissions.manage_messages:
        content_lower = message.content.lower()
        
        # Prüfe auf EXTREME Begriffe (INSTANT BAN)
        for word in EXTREME_WORDS:
            if word in content_lower:
                try:
                    await message.delete()
                except:
                    pass
                
                try:
                    await message.author.ban(reason=f"Auto-Ban: Verwendung von extremen/verbotenen Begriffen ({word})")
                except:
                    pass
                
                if AUTO_REPORT_CHANNEL_ID != 0:
                    report_channel = bot.get_channel(AUTO_REPORT_CHANNEL_ID)
                    if report_channel:
                        embed = discord.Embed(
                            title="🚨 AUTO-BAN DURCHGEFÜHRT",
                            description=f"**User:** {message.author.mention} ({message.author.name})\n"
                                       f"**User-ID:** {message.author.id}\n"
                                       f"**Channel:** {message.channel.mention}\n"
                                       f"**Grund:** Verwendung von extremen Begriffen",
                            color=discord.Color.dark_red(),
                            timestamp=datetime.utcnow()
                        )
                        embed.add_field(name="🚫 Nachricht", value=f"||{message.content[:1000]}||", inline=False)
                        embed.add_field(name="⚠️ Gefundenes Wort", value=f"||{word}||", inline=False)
                        embed.set_footer(text="Automatischer Schutz aktiviert")
                        await report_channel.send(embed=embed)
                
                return
        
        # Prüfe auf normale BLACKLIST Wörter (REPORT)
        found_words = []
        for word in BLACKLIST_WORDS:
            if word in content_lower and word not in EXTREME_WORDS:
                found_words.append(word)
        
        if found_words:
            try:
                await message.delete()
            except:
                pass
            
            warning = await message.channel.send(
                f"⚠️ {message.author.mention}, deine Nachricht wurde entfernt, da sie gegen die Regeln verstößt!"
            )
            await asyncio.sleep(5)
            try:
                await warning.delete()
            except:
                pass
            
            if AUTO_REPORT_CHANNEL_ID != 0:
                report_channel = bot.get_channel(AUTO_REPORT_CHANNEL_ID)
                if report_channel:
                    reports = load_reports()
                    report_id = f"{message.author.id}_{int(datetime.utcnow().timestamp())}"
                    
                    reports[report_id] = {
                        'user_id': message.author.id,
                        'message': message.content,
                        'channel_id': message.channel.id,
                        'timestamp': datetime.utcnow().isoformat(),
                        'found_words': found_words,
                        'status': 'pending'
                    }
                    save_reports(reports)
                    
                    embed = discord.Embed(
                        title="🚨 AUTO-MODERATION ALARM",
                        description=f"**User:** {message.author.mention} ({message.author.name})\n"
                                   f"**User-ID:** {message.author.id}\n"
                                   f"**Channel:** {message.channel.mention}",
                        color=discord.Color.orange(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="🚫 Nachricht (automatisch gelöscht)", value=f"||{message.content[:1000]}||", inline=False)
                    embed.add_field(name="⚠️ Gefundene Wörter", value=f"||{', '.join(found_words)}||", inline=False)
                    embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
                    embed.set_footer(text=f"Report-ID: {report_id}")
                    
                    view = ReportActionView(report_id, message.author.id)
                    await report_channel.send(embed=embed, view=view)
            
            return
    
    # LEVEL SYSTEM
    levels = load_levels()
    user_id = str(message.author.id)
    
    if user_id not in levels:
        levels[user_id] = {'xp': 0, 'level': 1, 'messages': 0}
    
    xp_gain = random.randint(15, 25)
    levels[user_id]['xp'] += xp_gain
    levels[user_id]['messages'] += 1
    
    xp = levels[user_id]['xp']
    lvl_start = levels[user_id]['level']
    lvl_end = int(xp ** (1/4))
    
    if lvl_start < lvl_end:
        levels[user_id]['level'] = lvl_end
        
        rewards = {
            5: "💬 Chatter",
            15: "⭐ Aktiv",
            30: "💎 Veteran",
            50: "🏆 Legende"
        }
        
        reward_text = ""
        if lvl_end in rewards:
            role = discord.utils.get(message.guild.roles, name=rewards[lvl_end])
            if role:
                try:
                    await message.author.add_roles(role)
                    reward_text = f"\n🎁 Du hast die Rolle **{rewards[lvl_end]}** erhalten!"
                except:
                    pass
        
        embed = discord.Embed(
            title="🎉 Level Up!",
            description=f"{message.author.mention} ist jetzt **Level {lvl_end}**! 🐼{reward_text}",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed, delete_after=10)
    
    save_levels(levels)
    await bot.process_commands(message)

# ===== REACTION ROLES SYSTEM =====
class ReactionRoleButton(Button):
    def __init__(self, role_name: str, emoji: str):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=role_name,
            emoji=emoji,
            custom_id=f"reaction_role_{role_name}"
        )
        self.role_name = role_name
    
    async def callback(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        
        if not role:
            await interaction.response.send_message(f"❌ Rolle '{self.role_name}' nicht gefunden!", ephemeral=True)
            return
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Rolle **{self.role_name}** entfernt!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Rolle **{self.role_name}** hinzugefügt!", ephemeral=True)

class ReactionRoleView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Benachrichtigungs-Rollen
        self.add_item(ReactionRoleButton("Stream-Ping", "🔴"))
        self.add_item(ReactionRoleButton("Ankündigungs-Ping", "📣"))
        self.add_item(ReactionRoleButton("Event-Ping", "🎉"))
        self.add_item(ReactionRoleButton("Giveaway-Ping", "🎁"))
        
        # Spiel-Rollen
        self.add_item(ReactionRoleButton("OPsucht Spieler", "🔮"))
        self.add_item(ReactionRoleButton("Händler", "💰"))

@bot.tree.command(name="reaction-setup", description="Erstellt das Reaction-Role System (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def reaction_setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎭 ROLLEN AUSWÄHLEN",
        description="Klicke auf die Buttons um deine Rollen zu bekommen!\n\n"
                   "**📣 Benachrichtigungen:**\n"
                   "🔴 **Stream-Ping** - Stream-Ankündigungen\n"
                   "📣 **Ankündigungs-Ping** - Wichtige Updates\n"
                   "🎉 **Event-Ping** - Community-Events\n"
                   "🎁 **Giveaway-Ping** - Giveaways\n\n"
                   "**🎮 Spiele:**\n"
                   "🔮 **OPsucht Spieler** - Für OPsucht-Spieler\n"
                   "💰 **Händler** - Handel & Wirtschaft",
        color=discord.Color.blue()
    )
    embed.set_footer(text="🐼 Panda's Karten Paradies")
    
    view = ReactionRoleView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Reaction-Role System erstellt!", ephemeral=True)

# ===== REPORT ACTION VIEW =====
class ReportActionView(View):
    def __init__(self, report_id, user_id):
        super().__init__(timeout=None)
        self.report_id = report_id
        self.user_id = user_id
    
    @discord.ui.button(label="✅ Bestrafen", style=discord.ButtonStyle.danger)
    async def accept_report(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Nur Mods können Reports bearbeiten!", ephemeral=True)
            return
        
        modal = PunishmentModal(self.report_id, self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⚠️ Verwarnen", style=discord.ButtonStyle.primary)
    async def warn_report(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Nur Mods können Reports bearbeiten!", ephemeral=True)
            return
        
        reports = load_reports()
        if self.report_id not in reports:
            await interaction.response.send_message("❌ Report nicht gefunden!", ephemeral=True)
            return
        
        warnings = load_warnings()
        user_id_str = str(self.user_id)
        
        if user_id_str not in warnings:
            warnings[user_id_str] = []
        
        warning = {
            'reason': f"Auto-Mod Report: Regelverstoß",
            'moderator': str(interaction.user.id),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        warnings[user_id_str].append(warning)
        save_warnings(warnings)
        
        reports[self.report_id]['status'] = 'warned'
        reports[self.report_id]['handled_by'] = interaction.user.id
        save_reports(reports)
        
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.yellow()
        embed.title = "⚠️ REPORT: VERWARNUNG ERTEILT"
        embed.add_field(name="Bearbeitet von", value=interaction.user.mention)
        
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message(f"✅ Verwarnung erteilt!", ephemeral=True)
    
    @discord.ui.button(label="❌ Ablehnen", style=discord.ButtonStyle.secondary)
    async def decline_report(self, interaction: discord.Interaction, button: Button):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Nur Mods können Reports bearbeiten!", ephemeral=True)
            return
        
        reports = load_reports()
        if self.report_id in reports:
            reports[self.report_id]['status'] = 'declined'
            reports[self.report_id]['handled_by'] = interaction.user.id
            save_reports(reports)
        
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.dark_grey()
        embed.title = "❌ REPORT: ABGELEHNT"
        
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message("✅ Report abgelehnt!", ephemeral=True)

class PunishmentModal(Modal):
    def __init__(self, report_id, user_id):
        super().__init__(title="Bestrafung")
        self.report_id = report_id
        self.user_id = user_id
        
        self.punishment = TextInput(
            label="Bestrafung (kick/timeout/ban)",
            placeholder="kick, timeout oder ban",
            required=True,
            max_length=10
        )
        
        self.reason = TextInput(
            label="Grund (optional)",
            placeholder="Zusätzlicher Grund...",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=500
        )
        
        self.duration = TextInput(
            label="Dauer in Minuten (nur bei timeout)",
            placeholder="z.B. 60",
            required=False,
            max_length=5
        )
        
        self.add_item(self.punishment)
        self.add_item(self.reason)
        self.add_item(self.duration)
    
    async def on_submit(self, interaction: discord.Interaction):
        punishment_type = self.punishment.value.lower()
        reason = self.reason.value or "Auto-Mod Report: Regelverstoß"
        
        user = interaction.guild.get_member(self.user_id)
        if not user:
            await interaction.response.send_message("❌ User nicht mehr auf dem Server!", ephemeral=True)
            return
        
        reports = load_reports()
        
        try:
            if punishment_type == "kick":
                await user.kick(reason=reason)
                action_text = "gekickt"
            elif punishment_type == "timeout":
                duration = int(self.duration.value) if self.duration.value else 60
                await user.timeout(discord.utils.utcnow() + timedelta(minutes=duration), reason=reason)
                action_text = f"Timeout ({duration} Min)"
            elif punishment_type == "ban":
                await user.ban(reason=reason)
                action_text = "gebannt"
            else:
                await interaction.response.send_message("❌ Ungültig! Nutze: kick, timeout oder ban", ephemeral=True)
                return
            
            reports[self.report_id]['status'] = 'punished'
            reports[self.report_id]['punishment'] = punishment_type
            save_reports(reports)
            
            embed = interaction.message.embeds[0]
            embed.color = discord.Color.red()
            embed.title = "🔨 REPORT: BESTRAFUNG DURCHGEFÜHRT"
            
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message(f"✅ User wurde {action_text}!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

# ===== LEVEL COMMANDS =====
@bot.tree.command(name="level", description="Zeigt dein Level")
@app_commands.describe(user="User (optional)")
async def level(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    levels = load_levels()
    user_id = str(user.id)
    
    if user_id not in levels:
        await interaction.response.send_message(f"{user.mention} hat noch keine XP!", ephemeral=True)
        return
    
    user_data = levels[user_id]
    current_level = user_data['level']
    next_level = current_level + 1
    xp_needed = (next_level ** 4) - user_data['xp']
    
    sorted_users = sorted(levels.items(), key=lambda x: x[1]['level'], reverse=True)
    rank = next((i for i, (uid, _) in enumerate(sorted_users, 1) if uid == user_id), None)
    
    embed = discord.Embed(title=f"📊 Level & Stats", color=user.color or discord.Color.blue())
    embed.set_author(name=user.display_name, icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.add_field(name="🏆 Level", value=f"```{current_level}```", inline=True)
    embed.add_field(name="⭐ XP", value=f"```{user_data['xp']}```", inline=True)
    embed.add_field(name="🎯 Rang", value=f"```#{rank}```", inline=True)
    embed.add_field(name="💬 Nachrichten", value=f"```{user_data.get('messages', 0)}```", inline=True)
    embed.add_field(name="📈 Nächstes Level", value=f"```{xp_needed} XP```", inline=True)
    embed.add_field(name="📊 Fortschritt", value=f"```{round((user_data['xp'] / (next_level ** 4)) * 100, 1)}%```", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="Zeigt die Top 10")
async def leaderboard(interaction: discord.Interaction):
    levels = load_levels()
    sorted_users = sorted(levels.items(), key=lambda x: x[1]['level'], reverse=True)[:10]
    
    embed = discord.Embed(
        title="🏆 Leaderboard - Top 10",
        description="Die aktivsten Community-Mitglieder!",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (user_id, data) in enumerate(sorted_users, 1):
        user = interaction.guild.get_member(int(user_id))
        if user:
            medal = medals[i-1] if i <= 3 else f"`#{i}`"
            embed.add_field(
                name=f"{medal} {user.display_name}",
                value=f"Level **{data['level']}** • {data['xp']} XP",
                inline=False
            )
    
    await interaction.response.send_message(embed=embed)

# ===== TICKET SYSTEM =====
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🎫 Ticket erstellen", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        existing_ticket = discord.utils.get(guild.text_channels, topic=f"Ticket von {interaction.user.id}")
        
        if existing_ticket:
            await interaction.response.send_message("❌ Du hast bereits ein Ticket!", ephemeral=True)
            return
        
        tickets = load_tickets()
        tickets['counter'] += 1
        ticket_number = tickets['counter']
        save_tickets(tickets)
        
        category = guild.get_channel(TICKET_CATEGORY_ID)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        if MOD_ROLE_ID != 0:
            mod_role = guild.get_role(MOD_ROLE_ID)
            if mod_role:
                overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        if SUPPORT_ROLE_ID != 0:
            support_role = guild.get_role(SUPPORT_ROLE_ID)
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        ticket_channel = await category.create_text_channel(
            name=f"ticket-{ticket_number}",
            overwrites=overwrites,
            topic=f"Ticket von {interaction.user.id}"
        )
        
        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_number}",
            description=f"Hallo {interaction.user.mention}!\n\n"
                       f"Ein Teammitglied wird sich bald um dein Anliegen kümmern.\n\n"
                       f"**Bitte beschreibe dein Problem so genau wie möglich!**",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Panda's Karten Paradies Support")
        
        close_view = TicketCloseView()
        await ticket_channel.send(f"{interaction.user.mention}", embed=embed, view=close_view)
        await interaction.response.send_message(f"✅ Ticket erstellt! → {ticket_channel.mention}", ephemeral=True)

class TicketCloseView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 Ticket schließen", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="🔒 Ticket wird geschlossen...",
            description="Channel wird in 5 Sekunden gelöscht.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.tree.command(name="ticket-setup", description="Erstellt Ticket-System (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Support-Ticket System",
        description="**Brauchst du Hilfe?**\n\n"
                   f"Klicke auf den Button um ein Support-Ticket zu erstellen.\n\n"
                   f"**Wofür?**\n"
                   f"• Fragen zum Server\n"
                   f"• Technische Probleme\n"
                   f"• Meldungen\n"
                   f"• Bewerbungen\n"
                   f"• Sonstiges",
        color=discord.Color.green()
    )
    embed.set_footer(text="🐼 Panda's Karten Paradies")
    
    view = TicketView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Ticket-System erstellt!", ephemeral=True)

# ===== GIVEAWAY SYSTEM =====
class GiveawayView(View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = message_id
    
    @discord.ui.button(label="🎉 Teilnehmen", style=discord.ButtonStyle.green, custom_id="join_giveaway")
    async def join_giveaway(self, interaction: discord.Interaction, button: Button):
        giveaways = load_giveaways()
        giveaway_id = str(self.message_id)
        
        if giveaway_id not in giveaways:
            await interaction.response.send_message("❌ Giveaway existiert nicht!", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        
        if user_id in giveaways[giveaway_id]['participants']:
            giveaways[giveaway_id]['participants'].remove(user_id)
            save_giveaways(giveaways)
            await interaction.response.send_message("❌ Du nimmst nicht mehr teil!", ephemeral=True)
        else:
            giveaways[giveaway_id]['participants'].append(user_id)
            save_giveaways(giveaways)
            await interaction.response.send_message("✅ Du nimmst teil! Viel Glück! 🍀", ephemeral=True)

@bot.tree.command(name="giveaway", description="Startet ein Giveaway (Owner)")
@app_commands.describe(prize="Preis", duration="Dauer in Minuten", winners="Gewinner")
async def giveaway(interaction: discord.Interaction, prize: str, duration: int, winners: int = 1):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Nur Owner!", ephemeral=True)
        return
    
    end_time = datetime.utcnow() + timedelta(minutes=duration)
    
    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"**Preis:** {prize}\n\n"
                   f"**Gewinner:** {winners}\n"
                   f"**Endet:** <t:{int(end_time.timestamp())}:R>\n\n"
                   f"Klicke auf 🎉!",
        color=discord.Color.gold(),
        timestamp=end_time
    )
    
    await interaction.response.send_message("✅ Wird erstellt...", ephemeral=True)
    
    view = GiveawayView(0)
    message = await interaction.channel.send(embed=embed, view=view)
    
    giveaways = load_giveaways()
    giveaways[str(message.id)] = {
        'prize': prize,
        'winners': winners,
        'end_time': end_time.isoformat(),
        'channel_id': interaction.channel.id,
        'host_id': interaction.user.id,
        'participants': []
    }
    save_giveaways(giveaways)
    
    view = GiveawayView(message.id)
    await message.edit(view=view)

@tasks.loop(seconds=30)
async def check_giveaways():
    giveaways = load_giveaways()
    current_time = datetime.utcnow()
    to_remove = []
    
    for giveaway_id, data in giveaways.items():
        end_time = datetime.fromisoformat(data['end_time'])
        
        if current_time >= end_time:
            channel = bot.get_channel(data['channel_id'])
            if channel:
                try:
                    message = await channel.fetch_message(int(giveaway_id))
                    participants = data['participants']
                    winners_count = min(data['winners'], len(participants))
                    
                    if winners_count == 0:
                        embed = discord.Embed(
                            title="🎉 Giveaway beendet!",
                            description=f"**Preis:** {data['prize']}\n\n❌ Keine Teilnehmer!",
                            color=discord.Color.red()
                        )
                        await message.edit(embed=embed, view=None)
                    else:
                        winners = random.sample(participants, winners_count)
                        winner_mentions = ", ".join([f"<@{uid}>" for uid in winners])
                        
                        embed = discord.Embed(
                            title="🎉 Giveaway beendet!",
                            description=f"**Preis:** {data['prize']}\n\n**Gewinner:** {winner_mentions}\n\nGlückwunsch! 🎊",
                            color=discord.Color.gold()
                        )
                        await message.edit(embed=embed, view=None)
                        await channel.send(f"🎉 Glückwunsch {winner_mentions}! Du hast **{data['prize']}** gewonnen!")
                except:
                    pass
            to_remove.append(giveaway_id)
    
    for giveaway_id in to_remove:
        del giveaways[giveaway_id]
    
    if to_remove:
        save_giveaways(giveaways)

# ===== VOICE COMMANDS =====
@bot.tree.command(name="voice-rename", description="Benenne deinen Channel um")
@app_commands.describe(name="Neuer Name")
async def voice_rename(interaction: discord.Interaction, name: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Du bist in keinem Voice!", ephemeral=True)
        return
    
    voice_channels = load_voice_channels()
    channel_id = str(interaction.user.voice.channel.id)
    
    if channel_id not in voice_channels:
        await interaction.response.send_message("❌ Kein temporärer Channel!", ephemeral=True)
        return
    
    if voice_channels[channel_id]['owner'] != interaction.user.id:
        await interaction.response.send_message("❌ Nicht dein Channel!", ephemeral=True)
        return
    
    if len(name) > 50:
        name = name[:50]
    
    await interaction.user.voice.channel.edit(name=f"🎮 {name}")
    await interaction.response.send_message(f"✅ Umbenannt zu: **{name}**", ephemeral=True)

@bot.tree.command(name="voice-limit", description="User-Limit setzen")
@app_commands.describe(limit="Anzahl (0 = unbegrenzt)")
async def voice_limit(interaction: discord.Interaction, limit: int):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Du bist in keinem Voice!", ephemeral=True)
        return
    
    voice_channels = load_voice_channels()
    channel_id = str(interaction.user.voice.channel.id)
    
    if channel_id not in voice_channels:
        await interaction.response.send_message("❌ Kein temporärer Channel!", ephemeral=True)
        return
    
    if voice_channels[channel_id]['owner'] != interaction.user.id:
        await interaction.response.send_message("❌ Nicht dein Channel!", ephemeral=True)
        return
    
    if limit < 0 or limit > 99:
        await interaction.response.send_message("❌ Limit: 0-99!", ephemeral=True)
        return
    
    await interaction.user.voice.channel.edit(user_limit=limit)
    
    if limit == 0:
        await interaction.response.send_message("✅ Limit entfernt!", ephemeral=True)
    else:
        await interaction.response.send_message(f"✅ Limit: **{limit}**", ephemeral=True)

@bot.tree.command(name="voice-lock", description="Sperre deinen Channel")
async def voice_lock(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Du bist in keinem Voice!", ephemeral=True)
        return
    
    voice_channels = load_voice_channels()
    channel_id = str(interaction.user.voice.channel.id)
    
    if channel_id not in voice_channels or voice_channels[channel_id]['owner'] != interaction.user.id:
        await interaction.response.send_message("❌ Nicht dein Channel!", ephemeral=True)
        return
    
    await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=False)
    await interaction.response.send_message("🔒 Channel gesperrt!", ephemeral=True)

@bot.tree.command(name="voice-unlock", description="Entsperre deinen Channel")
async def voice_unlock(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Du bist in keinem Voice!", ephemeral=True)
        return
    
    voice_channels = load_voice_channels()
    channel_id = str(interaction.user.voice.channel.id)
    
    if channel_id not in voice_channels or voice_channels[channel_id]['owner'] != interaction.user.id:
        await interaction.response.send_message("❌ Nicht dein Channel!", ephemeral=True)
        return
    
    await interaction.user.voice.channel.set_permissions(interaction.guild.default_role, connect=True)
    await interaction.response.send_message("🔓 Channel entsperrt!", ephemeral=True)

@bot.tree.command(name="voice-claim", description="Channel übernehmen")
async def voice_claim(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Du bist in keinem Voice!", ephemeral=True)
        return
    
    voice_channels = load_voice_channels()
    channel_id = str(interaction.user.voice.channel.id)
    
    if channel_id not in voice_channels:
        await interaction.response.send_message("❌ Kein temporärer Channel!", ephemeral=True)
        return
    
    owner_id = voice_channels[channel_id]['owner']
    owner = interaction.guild.get_member(owner_id)
    
    if owner and owner.voice and owner.voice.channel.id == int(channel_id):
        await interaction.response.send_message("❌ Owner ist noch da!", ephemeral=True)
        return
    
    voice_channels[channel_id]['owner'] = interaction.user.id
    save_voice_channels(voice_channels)
    await interaction.response.send_message("✅ Du bist jetzt Owner!", ephemeral=True)

# ===== MODERATION COMMANDS =====
@bot.tree.command(name="warn", description="Verwarnt einen User")
@app_commands.describe(user="User", reason="Grund")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
        return
    
    warnings = load_warnings()
    user_id = str(user.id)
    
    if user_id not in warnings:
        warnings[user_id] = []
    
    warning = {
        'reason': reason,
        'moderator': str(interaction.user.id),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    warnings[user_id].append(warning)
    save_warnings(warnings)
    
    embed = discord.Embed(
        title="⚠️ Verwarnung",
        description=f"{user.mention} wurde verwarnt!",
        color=discord.Color.orange(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Grund", value=reason, inline=False)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Verwarnungen", value=len(warnings[user_id]), inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kick", description="Kickt ein Mitglied")
@app_commands.describe(user="User", reason="Grund")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "Kein Grund"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
        return
    
    if user.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ Rolle zu hoch!", ephemeral=True)
        return
    
    await user.kick(reason=reason)
    await interaction.response.send_message(f"✅ {user.mention} wurde gekickt! Grund: {reason}")

@bot.tree.command(name="ban", description="Bannt ein Mitglied")
@app_commands.describe(user="User", reason="Grund")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Kein Grund"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
        return
    
    if user.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ Rolle zu hoch!", ephemeral=True)
        return
    
    await user.ban(reason=reason)
    await interaction.response.send_message(f"✅ {user.mention} wurde gebannt! Grund: {reason}")

@bot.tree.command(name="timeout", description="Gibt Timeout")
@app_commands.describe(user="User", duration="Minuten", reason="Grund")
async def timeout(interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = "Kein Grund"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
        return
    
    await user.timeout(discord.utils.utcnow() + timedelta(minutes=duration), reason=reason)
    await interaction.response.send_message(f"✅ {user.mention} hat {duration} Min Timeout! Grund: {reason}")

@bot.tree.command(name="clear", description="Löscht Nachrichten")
@app_commands.describe(amount="Anzahl")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Keine Berechtigung!", ephemeral=True)
        return
    
    if amount > 100:
        await interaction.response.send_message("❌ Max 100!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ {len(deleted)} Nachrichten gelöscht!")

# ===== FUN COMMANDS =====
@bot.tree.command(name="panda", description="Zeigt einen Panda!")
async def panda(interaction: discord.Interaction):
    pandas = [
        "🐼 *mampf* Bambus ist lecker!",
        "🐼 *rollt* Wheee!",
        "🐼 *klettert* So hoch!",
        "🐼 *schläft* Zzzzz...",
        "🐼 *winkt* Hallo!",
        "🐼 *kuschelt* 🤗"
    ]
    await interaction.response.send_message(random.choice(pandas))

@bot.tree.command(name="ping", description="Zeigt Latenz")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    emoji = "🟢" if latency < 100 else "🟡" if latency < 200 else "🔴"
    await interaction.response.send_message(f"🏓 Pong! {emoji} **{latency}ms**")

# ===== REPORT COMMAND =====
@bot.tree.command(name="report", description="Melde einen User wegen Regelverstoß")
@app_commands.describe(user="Der User", reason="Grund der Meldung")
async def report(interaction: discord.Interaction, user: discord.Member, reason: str):
    if user.bot:
        await interaction.response.send_message("❌ Du kannst keine Bots melden!", ephemeral=True)
        return
    
    if user.id == interaction.user.id:
        await interaction.response.send_message("❌ Du kannst dich nicht selbst melden!", ephemeral=True)
        return
    
    if user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Du kannst keine Mods/Admins melden!", ephemeral=True)
        return
    
    if AUTO_REPORT_CHANNEL_ID == 0:
        await interaction.response.send_message("❌ Report-System ist nicht konfiguriert!", ephemeral=True)
        return
    
    report_channel = bot.get_channel(AUTO_REPORT_CHANNEL_ID)
    if not report_channel:
        await interaction.response.send_message("❌ Report-Channel nicht gefunden!", ephemeral=True)
        return
    
    reports = load_reports()
    report_id = f"{user.id}_{int(datetime.utcnow().timestamp())}"
    
    reports[report_id] = {
        'user_id': user.id,
        'reporter_id': interaction.user.id,
        'reason': reason,
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'pending',
        'type': 'manual'
    }
    save_reports(reports)
    
    embed = discord.Embed(
        title="🚨 MANUELLE MELDUNG",
        description=f"**Gemeldeter User:** {user.mention} ({user.name})\n"
                   f"**User-ID:** {user.id}\n"
                   f"**Gemeldet von:** {interaction.user.mention}",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📋 Grund", value=reason, inline=False)
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.set_footer(text=f"Report-ID: {report_id}")
    
    view = ReportActionView(report_id, user.id)
    
    ping_text = ""
    if MOD_ROLE_ID != 0:
        ping_text = f"<@&{MOD_ROLE_ID}>"
    
    await report_channel.send(ping_text, embed=embed, view=view)
    await interaction.response.send_message("✅ Deine Meldung wurde an das Team weitergeleitet!", ephemeral=True)

# ===== WEITERE MOD COMMANDS =====
@bot.tree.command(name="warnings", description="Zeigt die Verwarnungen eines Users")
@app_commands.describe(user="Der User")
async def warnings_cmd(interaction: discord.Interaction, user: discord.Member):
    warnings = load_warnings()
    user_id = str(user.id)
    
    if user_id not in warnings or not warnings[user_id]:
        await interaction.response.send_message(f"{user.mention} hat keine Verwarnungen!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"⚠️ Verwarnungen von {user.display_name}",
        color=discord.Color.orange()
    )
    
    for i, warning in enumerate(warnings[user_id], 1):
        mod = interaction.guild.get_member(int(warning['moderator']))
        mod_name = mod.display_name if mod else "Unbekannt"
        timestamp = datetime.fromisoformat(warning['timestamp'])
        
        embed.add_field(
            name=f"Verwarnung #{i}",
            value=f"**Grund:** {warning['reason']}\n**Moderator:** {mod_name}\n**Datum:** {timestamp.strftime('%d.%m.%Y %H:%M')}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clearwarnings", description="Löscht alle Verwarnungen eines Users (Mod)")
@app_commands.describe(user="Der User")
async def clearwarnings(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    
    warnings = load_warnings()
    user_id = str(user.id)
    
    if user_id in warnings:
        del warnings[user_id]
        save_warnings(warnings)
    
    await interaction.response.send_message(f"✅ Alle Verwarnungen von {user.mention} wurden gelöscht!", ephemeral=True)

@bot.tree.command(name="reports", description="Zeigt alle offenen Reports (Mod)")
async def reports_cmd(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ Nur Mods können Reports sehen!", ephemeral=True)
        return
    
    reports = load_reports()
    pending_reports = {k: v for k, v in reports.items() if v['status'] == 'pending'}
    
    if not pending_reports:
        await interaction.response.send_message("✅ Keine offenen Reports!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📋 Offene Reports",
        description=f"Es gibt **{len(pending_reports)}** offene Report(s)",
        color=discord.Color.orange()
    )
    
    for i, (report_id, data) in enumerate(list(pending_reports.items())[:10], 1):
        user = interaction.guild.get_member(data['user_id'])
        user_text = user.mention if user else f"<@{data['user_id']}> (nicht mehr auf dem Server)"
        
        timestamp = datetime.fromisoformat(data['timestamp'])
        
        if data.get('type') == 'manual':
            reporter = interaction.guild.get_member(data['reporter_id'])
            reporter_text = reporter.mention if reporter else "Unbekannt"
            embed.add_field(
                name=f"#{i} - Manuelle Meldung",
                value=f"**User:** {user_text}\n**Gemeldet von:** {reporter_text}\n**Grund:** {data['reason']}\n**Zeit:** {timestamp.strftime('%d.%m. %H:%M')}",
                inline=False
            )
        else:
            words = ", ".join([f"||{w}||" for w in data.get('found_words', [])])
            embed.add_field(
                name=f"#{i} - Auto-Moderation",
                value=f"**User:** {user_text}\n**Wörter:** {words}\n**Zeit:** {timestamp.strftime('%d.%m. %H:%M')}",
                inline=False
            )
    
    if len(pending_reports) > 10:
        embed.set_footer(text=f"Zeige 10 von {len(pending_reports)} Reports")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="slowmode", description="Setzt einen Slowmode (Mod)")
@app_commands.describe(seconds="Sekunden (0 = aus)", channel="Channel (optional)")
async def slowmode(interaction: discord.Interaction, seconds: int, channel: discord.TextChannel = None):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    
    target_channel = channel or interaction.channel
    await target_channel.edit(slowmode_delay=seconds)
    
    if seconds == 0:
        await interaction.response.send_message(f"✅ Slowmode in {target_channel.mention} **deaktiviert**!", ephemeral=True)
    else:
        await interaction.response.send_message(f"✅ Slowmode in {target_channel.mention} auf **{seconds} Sekunden** gesetzt!", ephemeral=True)

@bot.tree.command(name="lock", description="Sperrt einen Channel (Mod)")
@app_commands.describe(channel="Channel (optional)")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    
    target_channel = channel or interaction.channel
    await target_channel.set_permissions(interaction.guild.default_role, send_messages=False)
    
    embed = discord.Embed(
        title="🔒 Channel gesperrt",
        description=f"Dieser Channel wurde von {interaction.user.mention} gesperrt.",
        color=discord.Color.red()
    )
    await target_channel.send(embed=embed)
    await interaction.response.send_message(f"✅ {target_channel.mention} wurde gesperrt!", ephemeral=True)

@bot.tree.command(name="unlock", description="Entsperrt einen Channel (Mod)")
@app_commands.describe(channel="Channel (optional)")
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ Du hast keine Berechtigung!", ephemeral=True)
        return
    
    target_channel = channel or interaction.channel
    await target_channel.set_permissions(interaction.guild.default_role, send_messages=True)
    
    embed = discord.Embed(
        title="🔓 Channel entsperrt",
        description=f"Dieser Channel wurde von {interaction.user.mention} entsperrt.",
        color=discord.Color.green()
    )
    await target_channel.send(embed=embed)
    await interaction.response.send_message(f"✅ {target_channel.mention} wurde entsperrt!", ephemeral=True)

# ===== INFO COMMANDS =====
@bot.tree.command(name="serverinfo", description="Zeigt Serverinformationen")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    
    embed = discord.Embed(
        title=f"📊 {guild.name}",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    
    embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Mitglieder", value=guild.member_count, inline=True)
    embed.add_field(name="💬 Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="🎭 Rollen", value=len(guild.roles), inline=True)
    embed.add_field(name="📅 Erstellt am", value=guild.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="🆙 Boosts", value=guild.premium_subscription_count, inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="Zeigt Userinformationen")
@app_commands.describe(user="Der User (optional)")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    
    roles = [role.mention for role in user.roles if role.name != "@everyone"]
    roles_text = ", ".join(roles) if roles else "Keine Rollen"
    
    embed = discord.Embed(
        title=f"👤 {user.display_name}",
        color=user.color,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    
    embed.add_field(name="📛 Username", value=f"{user.name}", inline=True)
    embed.add_field(name="🆔 ID", value=user.id, inline=True)
    embed.add_field(name="📅 Beitritt", value=user.joined_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="📆 Konto erstellt", value=user.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="🎭 Rollen", value=roles_text, inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="Zeigt das Avatar eines Users")
@app_commands.describe(user="Der User (optional)")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    
    embed = discord.Embed(
        title=f"🖼️ Avatar von {user.display_name}",
        color=user.color
    )
    embed.set_image(url=user.avatar.url if user.avatar else user.default_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="opsucht", description="Infos über OPsucht")
async def opsucht(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔮 OPsucht Server",
        description="**Der beste deutsche Minecraft-Server!**\n\n"
                   "Einer der größten und beliebtesten deutschen Minecraft-Server mit verschiedenen Spielmodi.",
        color=discord.Color.purple()
    )
    embed.add_field(name="📡 Server-IP", value="```opsucht.net```", inline=False)
    embed.add_field(name="🌐 Website", value="[opsucht.net](https://opsucht.net)", inline=True)
    embed.add_field(name="👥 Discord", value="[discord.gg/opsucht](https://discord.gg/opsucht)", inline=True)
    embed.set_footer(text="🐼 Wir zocken zusammen auf OPsucht!")
    await interaction.response.send_message(embed=embed)

# ===== OWNER COMMANDS =====
@bot.tree.command(name="announce", description="Sendet eine Ankündigung (Owner)")
@app_commands.describe(
    title="Titel der Ankündigung",
    message="Nachricht",
    channel="Channel (optional, sonst aktueller Channel)"
)
async def announce(interaction: discord.Interaction, title: str, message: str, channel: discord.TextChannel = None):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Nur der Owner kann Ankündigungen senden!", ephemeral=True)
        return
    
    target_channel = channel or interaction.channel
    
    embed = discord.Embed(
        title=f"📣 {title}",
        description=message,
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Panda's Karten Paradies", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    
    await target_channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Ankündigung gesendet in {target_channel.mention}!", ephemeral=True)

@bot.tree.command(name="embed", description="Erstellt ein Custom Embed (Owner)")
@app_commands.describe(
    title="Titel",
    description="Beschreibung",
    color="Farbe (hex, z.B. #FF5733)",
    channel="Channel (optional)"
)
async def embed_cmd(interaction: discord.Interaction, title: str, description: str, color: str = "#5865F2", channel: discord.TextChannel = None):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Nur der Owner kann Embeds erstellen!", ephemeral=True)
        return
    
    target_channel = channel or interaction.channel
    
    try:
        color_int = int(color.replace("#", ""), 16)
    except:
        color_int = 0x5865F2
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color(color_int),
        timestamp=datetime.utcnow()
    )
    
    await target_channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Embed gesendet in {target_channel.mention}!", ephemeral=True)

@bot.tree.command(name="serverstats", description="Zeigt erweiterte Server-Statistiken (Owner)")
async def serverstats(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Nur der Owner kann Server-Stats sehen!", ephemeral=True)
        return
    
    guild = interaction.guild
    
    online = sum(1 for m in guild.members if m.status != discord.Status.offline)
    bots = sum(1 for m in guild.members if m.bot)
    humans = guild.member_count - bots
    
    levels = load_levels()
    total_xp = sum(data['xp'] for data in levels.values())
    total_messages = sum(data.get('messages', 0) for data in levels.values())
    
    embed = discord.Embed(
        title=f"📊 {guild.name} - Erweiterte Statistiken",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    
    embed.add_field(name="👥 Mitglieder", value=f"```Gesamt: {guild.member_count}\nMenschen: {humans}\nBots: {bots}\nOnline: {online}```", inline=False)
    embed.add_field(name="💬 Channels", value=f"```Text: {len(guild.text_channels)}\nVoice: {len(guild.voice_channels)}\nGesamt: {len(guild.channels)}```", inline=True)
    embed.add_field(name="🎭 Rollen", value=f"```{len(guild.roles)}```", inline=True)
    embed.add_field(name="📊 Activity", value=f"```XP: {total_xp:,}\nNachrichten: {total_messages:,}```", inline=False)
    embed.add_field(name="🆙 Boosts", value=f"```Level {guild.premium_tier}\n{guild.premium_subscription_count} Boosts```", inline=True)
    embed.add_field(name="📅 Erstellt", value=f"```{guild.created_at.strftime('%d.%m.%Y')}```", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="blacklist-add", description="Fügt ein Wort zur Blacklist hinzu (Owner)")
@app_commands.describe(word="Das Wort", extreme="Ist es ein extremes Wort? (Auto-Ban)")
async def blacklist_add(interaction: discord.Interaction, word: str, extreme: bool = False):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Nur der Owner kann die Blacklist bearbeiten!", ephemeral=True)
        return
    
    word_lower = word.lower()
    
    if extreme:
        if word_lower not in EXTREME_WORDS:
            EXTREME_WORDS.append(word_lower)
            if word_lower not in BLACKLIST_WORDS:
                BLACKLIST_WORDS.append(word_lower)
            await interaction.response.send_message(f"✅ `{word}` wurde zur **EXTREME** Blacklist hinzugefügt (Auto-Ban)!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ `{word}` ist bereits in der Extreme-Liste!", ephemeral=True)
    else:
        if word_lower not in BLACKLIST_WORDS:
            BLACKLIST_WORDS.append(word_lower)
            await interaction.response.send_message(f"✅ `{word}` wurde zur Blacklist hinzugefügt (Report)!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ `{word}` ist bereits in der Liste!", ephemeral=True)

@bot.tree.command(name="blacklist-remove", description="Entfernt ein Wort von der Blacklist (Owner)")
@app_commands.describe(word="Das Wort")
async def blacklist_remove(interaction: discord.Interaction, word: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Nur der Owner kann die Blacklist bearbeiten!", ephemeral=True)
        return
    
    word_lower = word.lower()
    
    removed = False
    if word_lower in BLACKLIST_WORDS:
        BLACKLIST_WORDS.remove(word_lower)
        removed = True
    
    if word_lower in EXTREME_WORDS:
        EXTREME_WORDS.remove(word_lower)
        removed = True
    
    if removed:
        await interaction.response.send_message(f"✅ `{word}` wurde von der Blacklist entfernt!", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ `{word}` war nicht in der Liste!", ephemeral=True)

@bot.tree.command(name="blacklist-show", description="Zeigt die Blacklist (Owner)")
async def blacklist_show(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Nur der Owner kann die Blacklist sehen!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📋 Blacklist Übersicht",
        color=discord.Color.dark_red()
    )
    
    extreme_list = "\n".join([f"• ||{word}||" for word in EXTREME_WORDS[:25]])
    if len(EXTREME_WORDS) > 25:
        extreme_list += f"\n... und {len(EXTREME_WORDS) - 25} weitere"
    
    normal_list = "\n".join([f"• ||{word}||" for word in BLACKLIST_WORDS if word not in EXTREME_WORDS][:25])
    remaining = [w for w in BLACKLIST_WORDS if w not in EXTREME_WORDS]
    if len(remaining) > 25:
        normal_list += f"\n... und {len(remaining) - 25} weitere"
    
    embed.add_field(
        name="🚨 EXTREME Wörter (Auto-Ban)",
        value=extreme_list or "Keine",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Normale Wörter (Report)",
        value=normal_list or "Keine",
        inline=False
    )
    
    embed.set_footer(text=f"Gesamt: {len(BLACKLIST_WORDS)} Wörter | Extreme: {len(EXTREME_WORDS)}")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ===== BOT STARTEN =====
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN', 'DEIN_BOT_TOKEN_HIER')
    
    if TOKEN == 'DEIN_BOT_TOKEN_HIER':
        print("❌ FEHLER: Bot-Token fehlt!")
        print("Erstelle .env Datei mit: DISCORD_TOKEN=dein_token")
    else:
        try:
            keep_alive()  # Startet Webserver für 24/7 Uptime
            bot.run(TOKEN)
        except Exception as e:
            print(f"❌ Fehler: {e}")
