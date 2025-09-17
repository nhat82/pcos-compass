document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var modal = document.getElementById('eventModal');
    var eventForm = document.getElementById('eventForm');
    var cancelBtn = document.getElementById('cancelBtn');
    var deleteBtn = document.getElementById('deleteBtn');
    var modalTitle = document.getElementById('modalTitle');
    
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth'
        },
        events: '/logs/data',
        selectable: true,
        allDay: true,
        editable: true,
        eventStartEditable: true,
        dragScroll: true,
        
        eventDurationEditable: true,
        displayEventTime: false, // Hide event times


        // Style events by type
        eventDidMount: function(info) {
        const type = info.event.extendedProps.type;
        if (type === "PERIOD") {
            info.el.style.backgroundColor = "#BD290F";
            info.el.style.borderColor = "#BD290F";
        } else if (type === "OVULATION") {
            info.el.style.backgroundColor = "#42CAFD";
            info.el.style.borderColor = "#42CAFD";
        } else if (type === "NOTE") {
            info.el.style.backgroundColor = "#136F63";
            info.el.style.borderColor = "#136F63";
        }
        },

        // Create event - Show form instead of prompt
        select: function(info) {
            showEventForm('create', null, info);
        },

        // Edit event - Show form instead of prompt
        eventClick: function(info) {
            showEventForm('edit', info.event);
        },

        // Drag & Drop move
        eventDrop: function(info) {
            updateEvent(info.event);
        },

        // Resize event
        eventResize: function(info) {
            updateEvent(info.event);
        }
    });

    calendar.render();

    // Show/hide modal
    cancelBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Handle form submission
    eventForm.addEventListener('submit', function(e) {
        e.preventDefault();
        saveEvent();
    });

    // Handle delete
    deleteBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to delete this log?')) {
            deleteEvent();
        }
    });

    // Function to show event form
    function showEventForm(action, event = null, selectionInfo = null) {
        modalTitle.textContent = action === 'create' ? 'Create Log' : 'Edit Log';
        deleteBtn.style.display = action === 'edit' ? 'block' : 'none';
        
        if (action === 'create') {
            // Pre-fill form with selection data
            document.getElementById('eventId').value = '';
            document.getElementById('eventType').value = 'PERIOD';
            document.getElementById('eventDescription').value = '';
            
            // Handle FullCalendar's exclusive end date by adjusting it
            const startDate = selectionInfo.start;
            let endDate = selectionInfo.end;
            
            // For multi-day selections, adjust end date to be inclusive
            /*
            if (endDate) {
                endDate = new Date(endDate);
                endDate.setDate(endDate.getDate() - 1);
                console.log("Create not same day" + endDate);
                document.getElementById('eventEndDate').value = formatDate(endDate);
            } else {
                endDate = startDate; // Single day selection
                console.log("Create same day" + endDate);
            }
            */
            
            // Set date inputs (no time)
            document.getElementById('eventStartDate').value = formatDate(startDate);
            endDate = new Date(endDate);
            endDate.setDate(endDate.getDate());
            document.getElementById('eventEndDate').value = formatDate(endDate);
        } else {
            // Pre-fill form with event data
            document.getElementById('eventId').value = event.id;
            document.getElementById('eventType').value = event.extendedProps.type || 'PERIOD';
            document.getElementById('eventDescription').value = event.extendedProps.description || '';
            
            // Set date inputs (no time)
            document.getElementById('eventStartDate').value = formatDate(event.start);
            document.getElementById('eventEndDate').value = formatDate(event.end);

            /*
            let end = event.end || event.start;
            if (isSameDay(event.start, end)) {
                end = event.start; // Single day event
                document.getElementById('eventEndDate').value = formatDate(end);
                console.log("Prefill same day" + end);
            }
            else {
                end = new Date(end);
                end.setDate(end.getDate()); 
                document.getElementById('eventEndDate').value = formatDate(end);
                console.log("Prefill not same day" + end);
            }
                */
        }
        
        modal.style.display = 'flex';
    }

    // Helper function to check if two dates are the same day
    function isSameDay(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }

    // Format date for date input (YYYY-MM-DD)
    function formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // Save event (create or update)
    function saveEvent() {
        const eventId = document.getElementById('eventId').value;
        const method = eventId ? 'PUT' : 'POST';
        const url = eventId ? '/logs/' + eventId : '/logs';

        // Get form values
        const type = document.getElementById('eventType').value;
        const description = document.getElementById('eventDescription').value;
        const startDateInput = document.getElementById('eventStartDate').value;
        const endDateInput = document.getElementById('eventEndDate').value;

        // Convert to Date objects
        const startDateObj = new Date(startDateInput);
        let endDateObj = new Date(endDateInput);

        console.log("Save start date: " + startDateObj);
        console.log("Save end date: " + endDateObj);

        /*
        if (!isSameDay(startDateObj, endDateObj)) {
            endDateObj.setDate(endDateObj.getDate());
        }
        else {
            endDateObj = startDateObj; // Single day event
        }
        */

        const formData = {
            type: type,
            description: description,
            start_date: startDateObj.toISOString(),
            end_date: endDateObj.toISOString()
        };

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                calendar.refetchEvents(); // Refresh calendar
                modal.style.display = 'none';
            } else {
                alert('Failed to save log: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            alert('Error: ' + error.message);
        });
    }
    
    
    // Delete event
    function deleteEvent() {
        const eventId = document.getElementById('eventId').value;
        
        fetch('/logs/' + eventId, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                calendar.refetchEvents(); // Refresh all events
                modal.style.display = 'none';
            } else {
                alert('Failed to delete log: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            alert('Error: ' + error.message);
        });
    }

    // Update event (for drag/drop and resize)
    function updateEvent(event) {
        const startDateObj = event.start;
        let endDateObj = event.end || event.start;

        // Adjust end date for all-day events (inclusive)
        endDateObj = new Date(endDateObj);
        endDateObj.setDate(endDateObj.getDate() - 1);

        const formData = {
            title: event.title || event.extendedProps.description || event.extendedProps.type,
            start: startDateObj.toISOString(),
            end: endDateObj.toISOString()
        };

        fetch('/logs/' + event.id, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert('Failed to update log: ' + (data.error || 'Unknown error'));
                event.revert(); // Revert on failure
            }
        })
        .catch(error => {
            alert('Error: ' + error.message);
            event.revert();
        });
    }
});