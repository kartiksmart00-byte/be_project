document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    const contactInput = document.querySelector("input[name='contact_no']");

    form.addEventListener("submit", function(e) {
        const contact = contactInput.value.trim();
        if (!/^\d{10}$/.test(contact)) {
            e.preventDefault();
            alert("Please enter a valid 10-digit contact number.");
        }
    });
});


document.addEventListener("DOMContentLoaded", function() {
    const toggleAll = document.getElementById("toggleAll");
    const fields = [
        document.getElementById("current_password"),
        document.getElementById("new_password"),
        document.getElementById("confirm_password")
    ];

    toggleAll.addEventListener("change", function() {
        fields.forEach(field => {
            field.type = toggleAll.checked ? "text" : "password";
        });
    });
});