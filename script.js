document.addEventListener("DOMContentLoaded", () => {
    const leagueSelect = document.getElementById("league-select");
    const team1Select = document.getElementById("team1-select");
    const team2Select = document.getElementById("team2-select");
    const compareBtn = document.getElementById("compare-btn");
    const resultDiv = document.getElementById("comparison-result");
    const downloadBtn = document.getElementById("download-btn");

    let allData = {};
    let selectedLeague = "";
    let teamNames = [];

    const sections = {
        "Team Stats": [
            "FotMob Rating",
            "Goals (per match)",
            "Expected Goals (xG)",
            "Goals Conceded (per match)",
            "xG Conceded",
            "Touches in Opposition Box",
            "Shots on Target (per match)",
            "Big Chances",
            "Big Chances Missed",
            "Possession Won Final 3rd (per match)",
            "Average Possession",
            "Corners",
            "Accurate Crosses (per match)",
            "Accurate Long Balls (per match)",
            "Accurate Passes (per match)",
            "Penalties Awarded",
            "Penalties Conceded",
            "Interceptions (per match)",
            "Successful Tackles (per match)",
            "Clearances (per match)",
            "Saves (per match)",
            "Clean Sheets",
            "Fouls (per match)",
            "Yellow Cards",
            "Red Cards"
        ]
    };

    leagueSelect.addEventListener("change", () => {
        selectedLeague = leagueSelect.value;
        team1Select.innerHTML = '<option value="" disabled selected>Select team...</option>';
        team2Select.innerHTML = '<option value="" disabled selected>Select team...</option>';
        resultDiv.innerHTML = "";
        compareBtn.disabled = true;

        team1Select.disabled = false;
        team2Select.disabled = false;

        fetchDataForLeague(selectedLeague);
    });

    function fetchDataForLeague(leagueName) {
        fetch(`jsons/${leagueName}.json`)
            .then(response => response.json())
            .then(data => {
                allData = data;
                teamNames = Object.keys(data[Object.keys(data)[0]]);
                teamNames.forEach(team => {
                    const option1 = document.createElement("option");
                    option1.value = team;
                    option1.textContent = team;
                    team1Select.appendChild(option1);

                    const option2 = document.createElement("option");
                    option2.value = team;
                    option2.textContent = team;
                    team2Select.appendChild(option2);
                });

                compareBtn.disabled = false;
            })
            .catch(error => {
                console.error("Error loading data:", error);
            });
    }

    compareBtn.addEventListener("click", () => {
        const team1 = team1Select.value;
        const team2 = team2Select.value;

        if (team1 === team2) {
            alert("Please choose different teams.");
            return;
        }

        const comparisonData = {};
        for (const stat in allData) {
            comparisonData[stat] = {
                [team1]: allData[stat][team1],
                [team2]: allData[stat][team2]
            };
        }

        displayComparison(comparisonData, team1, team2);
    });

    function displayComparison(comparisonData, team1, team2) {
        resultDiv.innerHTML = "<h2>Results</h2>";
        const table = document.createElement("table");

        table.innerHTML = `
        <tr>
            <th>Stats</th>
            <th><img src="${allData["Takım Resmi"][team1]}" alt="${team1}" class="player-image" /> ${team1}</th>
            <th><img src="${allData["Takım Resmi"][team2]}" alt="${team2}" class="player-image" /> ${team2}</th>
        </tr>`;

        const lowerIsBetterStats = [
            "Big Chances Missed",
            "Fouls (per match)",
            "Goals Conceded (per match)",
            "Penalties Conceded",
            "xG Conceded",
            "Yellow Cards",
            "Red Cards"
        ];

        for (const section in sections) {
            sections[section].forEach(stat => {
                if (comparisonData[stat]) {
                    const row = document.createElement("tr");
                    const value1 = comparisonData[stat][team1];
                    const value2 = comparisonData[stat][team2];

                    const cell1Class = lowerIsBetterStats.includes(stat) ? (value1 < value2 ? 'highlight' : '') : (value1 > value2 ? 'highlight' : '');
                    const cell2Class = lowerIsBetterStats.includes(stat) ? (value2 < value1 ? 'highlight' : '') : (value2 > value1 ? 'highlight' : '');

                    row.innerHTML = `
                        <td>${stat}</td>
                        <td class="${cell1Class}">${value1}</td>
                        <td class="${cell2Class}">${value2}</td>`;
                    table.appendChild(row);
                }
            });
        }

        resultDiv.appendChild(table);
        downloadBtn.disabled = false;
    }

    downloadBtn.addEventListener("click", function() {
        const resultContainer = document.getElementById("comparison-result");
        html2canvas(resultContainer.querySelector("table")).then(canvas => {
            const link = document.createElement('a');
            link.download = 'comparison_table.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        });
    });
});