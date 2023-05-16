from flask import Flask, redirect, url_for, session, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import os
import openai
import requests
from bs4 import BeautifulSoup
import socket

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Set OpenAI API key
openai.api_key = "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"


def scrape_conference_guidelines(conference_name):
    # TODO: Implement web scraping for conference guidelines
    return "Guidelines for " + conference_name


def scrape_previous_talks(conference_name, year):
    # TODO: Implement web scraping for previous talks
    return [
        "Talk1 from " + conference_name + " " + str(year),
        "Talk2 from " + conference_name + " " + str(year),
    ]


@app.route("/feedback", methods=["POST"])
def feedback():
    rating = request.form.get("rating")
    feedback = request.form.get("feedback")

    # Here you might want to store this feedback in a database or process it in some way

    flash("Thank you for your feedback!", "success")
    return redirect(url_for("index"))


@app.route("/feedback", methods=["GET"])
def feedback_get():
    return redirect(url_for("index"))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        talk_type = request.form.get("talk_type")
        idea = request.form.get("idea")
        conference = request.form.get("conference")
        year = int(request.form.get("year"))
        level = request.form.get("level")  # Added this line

        # Check that all fields are filled in
        if not all(
            field is not None and field != ""
            for field in [talk_type, idea, conference, year]
        ):
            flash("Please fill in all fields", "error")
            return render_template("index.html")

        # Scrape guidelines and previous talks
        guidelines = scrape_conference_guidelines(conference)
        previous_talks = scrape_previous_talks(conference, year)

        # Prepare the prompt for OpenAI API
        prompt = f"""
First, generate a list of relevant talks from the {conference} conference in {year - 1} that relate to the following talk concept:
{idea}

Next, the speaker plans to give a {talk_type} at {conference} conference. The talk's level is {level}. The concept of the talk revolves around the following ideas:
{idea}

Based on this information, and it should have the following sections:

- Title of the talk: (Come up with something relevant based on previous talks at the conference.)
- Abstract: (Provide a brief summary of the talk here. This should be a concise representation of what will be discussed in the talk.)
- Outline: (Discuss the main points and progression of the talk here.)
- Prerequisites: (Specify what the audience should already know or do before the talk.)
- Audience: (Indicate who would benefit from this talk and why.)
"""

        # Generate proposal using OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003", prompt=prompt, max_tokens=500
        )

        response_text = response.choices[0].text.strip()
        relevant_talks, proposal = response_text.split("\n\n", 1)
        relevant_talks = relevant_talks.split("\n")[
            1:
        ]  # Skip the first line which is an instruction

        return render_template("index.html", proposal=proposal)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
