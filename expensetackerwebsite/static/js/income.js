//  const ctx = document.getElementById('myChart');
const ctx = document.getElementById('bar-chart');
let input = document.querySelector("#source")
let amount = document.querySelector("#amount")
let date = document.querySelector("#date")
let ulleft = document.querySelector(".list-left")
let ulright = document.querySelector(".list-right")
let datearr = []
let amountarr = []
let categoryarr = []


let incomechart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: chartLabels, 
    datasets: [{
      label: 'Income',
      data: chartValues,
      borderWidth: 1,
      barThickness: 50,
      backgroundColor: 'rgba(75, 192, 192, 0.6)'
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        suggestedMax: 100000,
        ticks: { stepSize: 10000 }
      }
    }
  }
});

document.addEventListener("DOMContentLoaded", function() {
  const dropdown = document.getElementById("incomeDropdown");
  const sourceInput = document.getElementById("source");

  dropdown.addEventListener("change", function() {
      sourceInput.value = dropdown.value;
  });
});

document.addEventListener("DOMContentLoaded", function() {
    const addIncomeBtn = document.getElementById("addIncomeBtn");
    const addIncomeBox = document.getElementById("addIncomeBox");

    addIncomeBtn.addEventListener("click", function(){
        addIncomeBox.style.display = (addIncomeBox.style.display === "none" || addIncomeBox.style.display === "") 
            ? "block" : "none";
    });

    document.querySelector(".remove").addEventListener("click", () => {
          document.querySelector(".INCOME-ADDFORM").style.display = " none";
    }); 
    
    const reportBtnIncome = document.getElementById("reportBtnIncome");
    const reportOptionsIncome = document.getElementById("reportOptionsIncome");

    reportBtnIncome.addEventListener("click", function(){
        reportOptionsIncome.style.display = (reportOptionsIncome.style.display === "none" || reportOptionsIncome.style.display === "") 
            ? "block" : "none";
    });
});

document.querySelector("#myform").addEventListener("submit", async (e) => {
  e.preventDefault();

  let source = input.value;
  let amountVal = amount.value;
  let dateVal = date.value;

  if (source === "" || amountVal === "" || dateVal === "") {
    alert("Please fill the data");
    return;
  }


  let response = await fetch("/income", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `source=${source}&amount=${amountVal}&date=${dateVal}`
  });

  let text = await response.text();
  console.log("Server response:", text);

  let li = document.createElement("li");
  li.innerHTML = `
    <div class="ulset">
      <div class="li-set">
        <div class="category">${source}</div>
        <div class="date">${dateVal}</div>
      </div>
      <div class="amount-icon">
        <i class="fa-solid fa-arrow-trend-up"></i>
        <div class="amount">${amountVal}</div>
      </div>
    </div>
  `;

  if (ulleft.children.length <= ulright.children.length) {
    ulleft.appendChild(li);
  } else {
    ulright.appendChild(li);
  }

  incomechart.data.labels.push(dateVal);
  incomechart.data.datasets[0].data.push(amountVal);

  if (incomechart.data.labels.length > 5) {
    incomechart.data.labels.shift();
    incomechart.data.datasets[0].data.shift();
  }

  incomechart.update();

  input.value = "";
  amount.value = "";
  date.value = "";
});



