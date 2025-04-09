const express = require("express");
const bodyParser = require("body-parser")
const bcrypt = require('bcrypt');
const fs = require("fs");
const path = require("path");
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('db.db');
const saltRounds = 10;

const app = express();
const PORT = 3000;

app.use(bodyParser.urlencoded({ extended: false }));

app.get("/styles.css", (req, res) => {
    res.sendFile(path.join(__dirname, '/public/css/style-main.css'));
});

app.use("/import", express.static(path.join(__dirname, "public/import")));

app.get("/view/:name", (req, res) => {
    res.sendFile(path.join(__dirname, '/public/view.html'));
});

app.get("/api/champions", (req, res) => {
    fs.readFile("character.json", "utf8", (err, data) => {
        if (err) {
            res.status(500).json({ error: "Failed to load champions" });
            return;
        }
        res.json(JSON.parse(data));
    });
});

app.get("/api/cocktails", (req, res) => {
    const championName = req.query.champion;
    fs.readFile("cocktail.json", "utf8", (err, data) => {
        if (err) {
            res.status(500).json({ error: "Failed to load cocktails" });
            return;
        }

        const cocktails = JSON.parse(data);
        const filteredCocktails = cocktails.filter(cocktail => cocktail.Champion === championName);
        res.json(filteredCocktails);
    });
});

app.post("/api/user", (req, res) => {

    bcrypt.hash(req.body.UserPassword, saltRounds, function(err, hash) {
        if (err != nil) {
            console.log(err);
        }
        db.run('INSERT INTO user(username, email, password) VALUES($username, $email, $password)', {
            $username: req.body.Username,
            $email: req.body.UserMail,
            $password: hash,
        });
    });

    res.redirect('/register');
})

app.get("/register", (req, res) => {
    res.sendFile(path.join(__dirname, '/public/register.html'));
})

app.use(express.static("public"));

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
