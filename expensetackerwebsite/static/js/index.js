
  const ctx1 = document.getElementById('dashboardchart');

  new Chart(ctx1, {
    type: 'doughnut',
    data: {
      labels: ['Total Balance', 'Total Income', 'Total Expense'],
      datasets: [{
        label: '# of Votes',
        data: [
          parseFloat(document.querySelector(".T-balance .t-amount").innerText.replace("₹","")),
          parseFloat(document.querySelector(".t-income .t-amount").innerText.replace("₹","")),
          parseFloat(document.querySelector(".t-expense .t-amount").innerText.replace("₹",""))

        ],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });


  document.addEventListener("DOMContentLoaded", function() {
    const reportBtnIncome = document.getElementById("reportBtnIncome");
    const reportOptionsIncome = document.getElementById("reportOptionsIncome");
  
    reportBtnIncome.addEventListener("click", function(){
        reportOptionsIncome.style.display = (reportOptionsIncome.style.display === "none" || reportOptionsIncome.style.display === "") 
            ? "block" : "none";
    });
  });


