// javascript.js

$(document).ready(function() {
    function updateWeekDays(startDate) {
        const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        const options = { month: '2-digit', day: '2-digit' };
        
        dayNames.forEach((dayName, index) => {
            const currentDay = new Date(startDate);
            currentDay.setDate(startDate.getDate() + index);
            $(`#${dayName.toLowerCase()}-date`).text(currentDay.toLocaleDateString('en-US', options));
        });
    }

    function setCurrentWeek() {
        const today = new Date();
        const dayOfWeek = today.getDay();
        const startDate = new Date(today);
        startDate.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));  // Get Monday of the current week

        updateWeekDays(startDate);
    }

    $('#week-select').datepicker({
        showWeek: true,
        firstDay: 1,
        onSelect: function(dateText, inst) {
            const date = $(this).datepicker('getDate');
            const startDate = new Date(date);
            startDate.setDate(startDate.getDate() - startDate.getDay() + 1);  // Adjust to Monday of the selected week

            updateWeekDays(startDate);
        },
        dateFormat: 'yy-mm-dd'
    });

    setCurrentWeek();  // Set current week dates on page load
});
function editNotes() {
    document.getElementById("notes-textarea").removeAttribute("readonly");
    document.getElementById("edit-notes").style.display = "none";
    document.getElementById("save-notes").style.display = "inline-block";
    document.getElementById("cancel-edit").style.display = "inline-block";
}

function cancelEdit() {
    document.getElementById("notes-textarea").setAttribute("readonly", "readonly");
    document.getElementById("edit-notes").style.display = "inline-block";
    document.getElementById("save-notes").style.display = "none";
    document.getElementById("cancel-edit").style.display = "none";

    // Reset the textarea content to the original notes value
    document.getElementById("notes-textarea").value = "{{ notes }}";
}
