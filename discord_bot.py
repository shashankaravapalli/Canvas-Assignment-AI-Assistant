import os
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Discord bot connected as {bot.user}")


@bot.command()
async def hello(ctx):
    await ctx.send(
        "👋 Hello! Canvas Assignment Assistant is online."
    )

@bot.command()
async def courses(ctx):
    await ctx.send("📚 Checking your Canvas courses...")

    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}"
    }

    try:
        url = f"{CANVAS_BASE_URL}/api/v1/courses"

        response = requests.get(
            url,
            headers=headers,
            params={"per_page": 100},
            timeout=10
        )

        response.raise_for_status()
        courses = response.json()

        if not courses:
            await ctx.send("No Canvas courses found.")
            return

        for course in courses:
            course_name = course.get("name")

            if course_name:
                await ctx.send(f"📘 {course_name}")

    except Exception as error:
        await ctx.send("⚠️ Unable to retrieve Canvas courses.")
        print(error)

        
@bot.command()
async def assignments(ctx):
    await ctx.send(
        "📚 Checking Canvas for your upcoming assignments..."
    )

    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}"
    }

    try:
        courses_url = f"{CANVAS_BASE_URL}/api/v1/courses"

        courses_response = requests.get(
            courses_url,
            headers=headers,
            params={
                "per_page": 100
            },
            timeout=10
        )

        courses_response.raise_for_status()
        courses = courses_response.json()

        all_assignments = []

        for course in courses:
            course_id = course["id"]
            course_name = course.get(
                "name",
                "Unknown Course"
            )

            assignments_url = (
                f"{CANVAS_BASE_URL}/api/v1/courses/"
                f"{course_id}/assignments"
            )

            assignments_response = requests.get(
                assignments_url,
                headers=headers,
                params={
                    "per_page": 100
                },
                timeout=10
            )

            if assignments_response.status_code == 200:
                assignments = assignments_response.json()

                for assignment in assignments:
                    due_at = assignment.get("due_at")

                    if not due_at:
                        continue

                    due_date = datetime.fromisoformat(
                     due_at.replace("Z", "+00:00")
                    )

                    if due_date < datetime.now(timezone.utc):
                        continue

                    all_assignments.append({
                        "course": course_name,
                        "name": assignment.get(
                        "name",
                        "Unnamed Assignment"
                        ),
                        "due": due_at
                    })

        if not all_assignments:
            await ctx.send(
                "🎉 No upcoming Canvas assignments found."
            )
            return

        for assignment in all_assignments:
            due = assignment["due"] or "No due date"

            await ctx.send(
                f"📘 **{assignment['course']}**\n"
                f"📝 {assignment['name']}\n"
                f"📅 Due: {due}"
            )

    except Exception as error:
        await ctx.send(
            "⚠️ Unable to retrieve Canvas assignments."
        )
        print(error)

@bot.command()
async def today(ctx):
    await ctx.send("📅 Checking Canvas assignments due today...")

    today_date = datetime.now(timezone.utc).date()
    today_assignments = []


    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}"
    }

    try:
        courses_response = requests.get(
            f"{CANVAS_BASE_URL}/api/v1/courses",
            headers=headers,
            params={"per_page": 100},
            timeout=10
        )

        courses_response.raise_for_status()
        courses = courses_response.json()

        for course in courses:
            course_id = course["id"]
            course_name = course.get("name", "Unknown Course")

            assignments_response = requests.get(
                f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/assignments",
                headers=headers,
                params={"per_page": 100},
                timeout=10
            )

            if assignments_response.status_code == 403:
                print(f"Skipping inaccessabile course: {course_name}")
                continue
            assignments = assignments_response.json()

            for assignment in assignments:
                due_at = assignment.get("due_at")

                if not due_at:
                    continue

                due_date = datetime.fromisoformat(
                    due_at.replace("Z", "+00:00")
                )

                if due_date.date() == today_date:
                    today_assignments.append({
                        "course": course_name,
                        "name": assignment.get("name", "Assignment"),
                        "due": due_at
                    })

        if not today_assignments:
            await ctx.send("🎉 No Canvas assignments due today.")
        else:
            await ctx.send(
                f"📚 You have {len(today_assignments)} assignment(s) due today:"
        )

            for assignment in today_assignments:
                due_date = datetime.fromisoformat(
                    assignment["due"].replace("Z", "+00:00")
                )
                due = due_date.strftime("%I:%M %p")

                await ctx.send(
                    f"📘 **{assignment['course']}**\n"
                    f"📝 {assignment['name']}\n"
                    f"⏰ Due: {due}"
                )

    except Exception as error:
        await ctx.send("⚠️ Unable to retrieve today's Canvas assignments.")
        print(error)


@bot.command()
async def week(ctx):
    await ctx.send("📅 Checking Canvas assignments due in the next 7 days...")

    start_date = datetime.now(timezone.utc)
    end_date = start_date + timedelta(days=7)
    week_assignments = []

    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}"
    }

    try:
        courses_response = requests.get(
            f"{CANVAS_BASE_URL}/api/v1/courses",
            headers=headers,
            params={"enrollment_state": "active",
                    "per_page": 100
            },
            timeout=10
        )

        courses_response.raise_for_status()
        courses = courses_response.json()

        for course in courses:
            course_id = course["id"]
            course_name = course.get("name", "Unknown Course")

            assignments_response = requests.get(
                f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/assignments",
                headers=headers,
                params={"per_page": 100},
                timeout=10
            )

            if assignments_response.status_code == 403:
                print(f"Skipping inaccessible course: {course_name}")
                continue

            assignments_response.raise_for_status()
            assignments = assignments_response.json()

    except Exception as error:
        await ctx.send(" Unable to retrieve this week's Canvas assignments.")
        print(error)

@bot.command()
async def testassignments(ctx):
    await ctx.send(
        "🧪 **Demo Assignments**\n\n"
        "📘 **MATH** — Homework 1 — Sep 20, 2026 11:59 PM\n"
        "💻 **CS 010B** — Programming Assignment — Sep 25, 2026 11:59 PM\n"
        "🤖 **Robotics** — Robot Lab — Sep 28, 2026 11:59 PM"
    )


@bot.command(name="commands")
async def show_commands(ctx):
    await ctx.send(
        "🤖 **Canvas Assignment Assistant Commands**\n\n"
        "📅 `!today` — Show assignments due today\n"
        "🗓️ `!week` — Show assignments due in the next 7 days\n"
        "📚 `!assignments` — Show upcoming Canvas assignments\n"
        "🧪 `!testassignments` — Show sample assignments for testing"
    )





bot.run(DISCORD_TOKEN)