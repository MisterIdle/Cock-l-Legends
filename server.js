const express = require("express");
const bodyParser = require("body-parser");
const bcrypt = require("bcrypt");
const fs = require("fs");
const path = require("path");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const PORT = 8080;
const saltRounds = 10;
const db = new sqlite3.Database("db.db");

app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, "public")));

app.use("/css", express.static(path.join(__dirname, "public/css")));
app.use("/js", express.static(path.join(__dirname, "public/js")));
app.use("/images", express.static(path.join(__dirname, "public/images")));
app.use("/import", express.static(path.join(__dirname, "public/import")));

app.get("/view", (req, res) => {
    const championName = req.query.name;
    if (!championName) {
        return res.status(400).send("Championship name is required");
    }
    res.sendFile(path.join(__dirname, "public/view.html"));
});

app.get("/register", (req, res) => {
    res.sendFile(path.join(__dirname, "public/register.html"));
});

app.get("/api/champions", (req, res) => {
    fs.readFile("character.json", "utf8", (err, data) => {
        if (err) {
            return res.status(500).json({ error: "Failed to load champions" });
        }
        try {
            const champions = JSON.parse(data);
            res.json(champions);
        } catch (parseErr) {
            res.status(500).json({ error: "Invalid JSON format in character.json" });
        }
    });
});

app.get("/api/cocktails", (req, res) => {
    const championName = req.query.champion;
    if (!championName) return res.status(400).json({ error: "Champion is required" });

    fs.readFile("cocktail.json", "utf8", (err, data) => {
        if (err) {
            return res.status(500).json({ error: "Failed to load cocktails" });
        }

        try {
            const cocktails = JSON.parse(data);
            const filtered = cocktails.filter(c => c.Champion === championName);
            res.json(filtered);
        } catch (parseErr) {
            res.status(500).json({ error: "Invalid JSON format in cocktail.json" });
        }
    });
});

app.post("/api/user", async (req, res) => {
    const { Username, UserMail, UserPassword } = req.body;
    if (!Username || !UserMail || !UserPassword) {
        return res.status(400).json({ error: "Missing required fields" });
    }

    try {
        const hash = await bcrypt.hash(UserPassword, saltRounds);
        db.run(
            `INSERT INTO user(username, email, password) VALUES (?, ?, ?)`,
            [Username, UserMail, hash],
            function (err) {
                if (err) {
                    console.error(err);
                    return res.status(500).json({ error: "Database error" });
                }
                res.redirect("/register");
            }
        );
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: "Encryption failed" });
    }
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
