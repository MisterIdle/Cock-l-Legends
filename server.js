const express = require("express");
const bodyParser = require("body-parser");
const bcrypt = require("bcrypt");
const fs = require("fs");
const path = require("path");
const sqlite3 = require("sqlite3").verbose();
const cookieParser = require("cookie-parser");


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
app.use(cookieParser("ILOVEPASTA"));

app.get("/view", (req, res) => {
    const championName = req.query.name;
    if (!championName) {
        return res.status(400).send("Championship name is required");
    }
    res.sendFile(path.join(__dirname, "public/view.html"));
});

app.get("/register", (req, res) => {
    if (req.signedCookies.user_id) {
        return res.redirect("/");
    }
    
    res.sendFile(path.join(__dirname, "public/register.html"));
});

app.get("/login", (req, res) => {
    if (req.signedCookies.user_id) {
        return res.redirect("/");
    }
    
    res.sendFile(path.join(__dirname, "public/login.html"));
});


app.get("/favorites", (req, res) => {
    res.sendFile(path.join(__dirname, "public/favorites.html"));
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


app.get("/api/session", (req, res) => {
    const userId = req.signedCookies.user_id;

    if (!userId) {
        return res.status(401).json({ error: "Unauthorized" });
    }

    db.get("SELECT username FROM user WHERE id = ?", [userId], (err, row) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: "Database error" });
        }

        if (!row) {
            return res.status(401).json({ error: "Invalid session" });
        }

        res.json({
            loggedIn: true,
            username: row.username
        });
    });
});

app.post("/api/register", async (req, res) => {
    const { Username, UserMail, UserPassword } = req.body;

    if (!Username || !UserMail || !UserPassword) {
        return res.status(400).json({ error: "Missing required fields" });
    }

    try {
        db.get(
            `SELECT * FROM user WHERE username = ? OR email = ?`,
            [Username, UserMail],
            async (err, row) => {
                if (err) {
                    console.error(err);
                    return res.status(500).json({ error: "Database error" });
                }

                if (row) {
                    return res.status(409).json({
                        error: "Username or email already exists"
                    });
                }

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
            }
        );
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: "Encryption failed" });
    }
});


app.post("/api/login", (req, res) => {
    const { UserMail, UserPassword } = req.body;
    if (!UserMail || !UserPassword) {
        return res.status(400).json({ error: "Missing email or password" });
    }

    db.get("SELECT * FROM user WHERE email = ?", [UserMail], async (err, user) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: "Database error" });
        }

        if (!user) {
            return res.status(401).json({ error: "Invalid credentials" });
        }

        const match = await bcrypt.compare(UserPassword, user.password);
        if (!match) {
            return res.status(401).json({ error: "Invalid credentials" });
        }

        res.cookie("user_id", user.id, { signed: true, httpOnly: true });
        res.redirect("http://localhost:8080");
        
        
    });
});

app.post("/api/favorites", (req, res) => {
    const userId = req.signedCookies.user_id;
    const { cocktailName } = req.body;

    if (!userId) return res.status(401).json({ error: "Not logged in" });
    if (!cocktailName) return res.status(400).json({ error: "No cocktail specified" });

    db.get(
        "SELECT * FROM favorites WHERE user_id = ? AND cocktail_name = ?",
        [userId, cocktailName],
        (err, row) => {
            if (err) {
                console.error(err);
                return res.status(500).json({ error: "Database error" });
            }

            if (row) {
                return res.status(409).json({ error: "Cocktail already in favorites" });
            }

            db.run(
                "INSERT INTO favorites (user_id, cocktail_name) VALUES (?, ?)",
                [userId, cocktailName],
                function (err) {
                    if (err) {
                        console.error(err);
                        return res.status(500).json({ error: "Database error" });
                    }
                    res.json({ message: "Cocktail favorited" });
                }
            );
        }
    );
});


app.get("/api/favorites", (req, res) => {
    const userId = req.signedCookies.user_id;
    if (!userId) return res.status(401).json({ error: "Not logged in" });

    db.all("SELECT cocktail_name FROM favorites WHERE user_id = ?", [userId], (err, rows) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: "Database error" });
        }
        res.json({ favorites: rows.map(row => row.cocktail_name) });
    });
});

app.post("/logout", (req, res) => {
    res.clearCookie("user_id");
    res.redirect("/");
});




app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
