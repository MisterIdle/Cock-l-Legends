const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = 3000;

app.use(express.static("public"));

app.get("/api/champions", (req, res) => {
    fs.readFile("character.json", "utf8", (err, data) => {
        if (err) {
            res.status(500).json({ error: "Failed to load champions" });
            return;
        }
        res.json(JSON.parse(data));
    });
});

// Endpoint pour récupérer les cocktails associés à un champion
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

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
