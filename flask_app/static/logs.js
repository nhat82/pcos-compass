document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var modal = document.getElementById('eventModal');
    var eventForm = document.getElementById('eventForm');
    var cancelBtn = document.getElementById('cancelBtn');
    var modalCloseBtn = document.getElementById('modalCloseBtn'); // X button
    var deleteBtn = document.getElementById('deleteBtn');
    var modalTitle = document.getElementById('modalTitle');
    var showTreatmentNames = false; 
    var toggleButton = document.getElementById('toggleLogDisplay');

    [cancelBtn, modalCloseBtn].forEach(btn => {
    if (btn) {
        btn.addEventListener('click', function() {
        modal.style.display = 'none';
        });
    }
    });


    if (!cancelBtn || !deleteBtn || !modalTitle || !eventForm) {
        console.error("Modal elements not found. Check your HTML IDs.");
        return;
    }

    // Get both create log buttons
    var createLogBtnSidebar = document.getElementById('createLogBtnSidebar');

    // Treatment options from your Python data
    const TREATMENTS = {
        "Metformin": {
            "description": "Used to improve insulin resistance, which can help regulate menstrual cycles and ovulation."
        },
        "Clomiphene (Clomid)": {
            "description": "An oral medication used to stimulate the pituitary gland to release hormones necessary to trigger ovulation."
        },
        "Letrozole (Femara)": {
            "description": "An aromatase inhibitor used off-label to stimulate ovulation, often with fewer side effects than Clomiphene."
        },
        "Birth Control Pills": {
            "description": "Combination pills used to regulate menstrual cycles, reduce androgen levels (acne, hair growth), and protect the uterine lining."
        },
        "Spironolactone": {
            "description": "A diuretic that also blocks the effects of androgens, used primarily to treat hirsutism (excessive hair growth) and acne."
        },
        "Eflornithine cream (Vaniqa)": {
            "description": "A prescription cream applied directly to the skin to slow down the growth of unwanted facial hair."
        },
        "Gonadotropins": {
            "description": "Injectable hormones (FSH and LH) used when oral fertility medications fail to directly stimulate the ovaries to produce eggs."
        },
        "Progestin therapy": {
            "description": "Progestin is taken periodically to induce a withdrawal bleed, protecting the uterus lining from the risk of endometrial hyperplasia."
        },
        "GLP-1 Receptor Agonists (e.g., Semaglutide)": {
            "description": "Injectable drugs used for weight management and blood sugar control, which can improve PCOS metabolic outcomes."
        },
        "Diet modification": {
            "description": "Focusing on low glycemic index (GI) foods, balanced carbohydrates, and healthy fats to manage blood sugar and insulin levels."
        },
        "Regular exercise": {
            "description": "Physical activity that improves insulin sensitivity, supports weight management, and boosts mood."
        },
        "Weight management": {
            "description": "Achieving and maintaining a healthy weight, which can significantly improve all PCOS symptoms, including hormonal balance and fertility."
        },
        "Myo-inositol": {
            "description": "A B-vitamin-like substance that acts as an insulin sensitizer, helping to improve egg quality and menstrual regularity."
        },
        "D-chiro-inositol": {
            "description": "Often combined with Myo-inositol, this supplement is part of the insulin signaling pathway and helps improve glucose metabolism."
        },
        "Vitamin D supplementation": {
            "description": "Used to correct common deficiencies in PCOS patients; may improve insulin sensitivity and support ovarian function."
        },
        "Omega-3 fatty acids": {
            "description": "Essential fats that help reduce inflammation and may improve lipid profiles and insulin resistance."
        },
        "Ovarian drilling": {
            "description": "A laparoscopic surgery where small holes are made in the ovaries to reduce androgen production and sometimes trigger ovulation."
        }
    };


    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth'
        },
        
        // Modified events function to handle toggle state
        events: function(fetchInfo, successCallback, failureCallback) {
            // Pass the current toggle state to the server
            fetch('/logs/data?show_treatments=' + showTreatmentNames)
                .then(response => response.json())
                .then(data => successCallback(data))
                .catch(error => failureCallback(error));
        },
        
        selectable: true,
        allDay: true,
        editable: true,
        eventStartEditable: true,
        dragScroll: true,
        eventDurationEditable: true,
        displayEventTime: false,

        // Style events by type
        eventDidMount: function(info) {
            const type = info.event.extendedProps.type;
            if (type === "Period") {
                info.el.style.backgroundColor = "#f15b8d";
                info.el.style.borderColor = "#f15b8d";
            } else if (type === "Ovulation") {
                info.el.style.backgroundColor = "#42CAFD";
                info.el.style.borderColor = "#42CAFD";
            } else if (type === "Sexual Activity") {
                info.el.style.backgroundColor = "#FF6B6B";
                info.el.style.borderColor = "#FF6B6B";
            } else if (type === "Event") {
                info.el.style.backgroundColor = "#f8d472";
                info.el.style.borderColor = "#f8d472";
            } else if (type === "Treatment") {
                info.el.style.backgroundColor = "#b2e0c3";
                info.el.style.borderColor = "#b2e0c3";
            }
        },

        // Custom event content to handle toggle display
        eventContent: function(arg) {
            let displayText;
            const type = arg.event.extendedProps.type;
            const description = arg.event.extendedProps.description;
            const treatmentName = arg.event.extendedProps.treatment_name;
            
            if (showTreatmentNames) {
                // When toggle is ON: Show event type + description for ALL events
                if (type === "Treatment" && treatmentName) {
                    // For treatment events, show type + treatment name + description
                    displayText = type + ": " + treatmentName;
                    if (description && description !== treatmentName) {
                        displayText += " - " + description;
                    }
                } else {
                    // For all other events, show type + description
                    displayText = type;
                    if (description) {
                        displayText += ": " + description;
                    }
                }
            } else {
                // When toggle is OFF: Show only description for ALL events
                if (type === "Treatment" && treatmentName) {
                    // For treatment events, show treatment name as description
                    displayText = treatmentName;
                    if (description && description !== treatmentName) {
                        displayText += " - " + description;
                    }
                } else {
                    // For all other events, show only description
                    displayText = description || type; // Fallback to type if no description
                }
            }
            
            return {
                html: `<div class="fc-event-title">${displayText}</div>`
            };
        },

        // Edit event - Show form when clicking on existing events
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
        },

        // Create event - Show form when selecting date range
        select: function(selectionInfo) {
            showEventForm('create', null, selectionInfo);
        }
    });


    calendar.render();

    // Toggle button functionality
    if (toggleButton) {
        toggleButton.addEventListener('click', function() {
            // 1. Update the internal state
            showTreatmentNames = !showTreatmentNames;
            
            // 2. Update the button's ARIA state for CSS styling (REQUIRED for the visual toggle)
            this.setAttribute('aria-checked', showTreatmentNames ? 'true' : 'false');
            
            // 3. (Optional) Remove the now redundant function call, 
            //    or keep it if you need to run specific logic there.
            //    The function below is now modified to update the ARIA status if needed elsewhere.
            updateToggleButtonState();
            
            // 4. Refresh the calendar to re-render event titles based on the new state
            refreshCalendarEvents();
        });
    }

    function updateToggleButtonState() {
        if (toggleButton) {
            // 5. Explicitly set the aria-checked state based on the variable
            toggleButton.setAttribute('aria-checked', showTreatmentNames ? 'true' : 'false');
            
            // 6. The textContent is empty in your prompt, so this line is redundant 
            //    unless you decide to add actual text content later.
            // toggleButton.textContent = showTreatmentNames ? '' : '';
        }
    }


    function refreshCalendarEvents() {
        calendar.refetchEvents();
    }

    // Add event listeners to create log buttons
    createLogBtnSidebar.addEventListener('click', function() {
        showEventForm('create');
    });

    // Show/hide modal
    cancelBtn.addEventListener('click', function() {
        modal.style.display = 'none';
        resetTreatmentFields();
    });

    // Handle form submission
    eventForm.addEventListener('submit', function(e) {
        e.preventDefault();
        saveEvent();
    });

    // Handle delete
    deleteBtn.addEventListener('click', function() {
        if (confirm('Are sure you want to delete this log?')) {
            deleteEvent();
        }
    });

    // Handle treatment type change
    document.getElementById('eventType').addEventListener('change', function() {
        toggleTreatmentFields(this.value);
    });

    // Function to toggle treatment-specific fields
// Handle treatment type change
    const eventTypeSelect = document.getElementById('eventType');
    eventTypeSelect.addEventListener('change', function() {
        toggleTreatmentFields(this.value);
    });
    
    // // Add the treatment select change listener *outside* of toggleTreatmentFields
    const treatmentSelect = document.getElementById('treatmentSelect');
    treatmentSelect.addEventListener('change', function() {
        const selectedTreatment = this.value;
        const treatmentDescription = document.getElementById('treatmentDescription');
        const customTreatmentGroup = document.getElementById('customTreatmentGroup');

        if (selectedTreatment && selectedTreatment !== 'custom' && TREATMENTS[selectedTreatment]) {
            treatmentDescription.textContent = TREATMENTS[selectedTreatment].description;
            treatmentDescription.style.display = 'block';
            customTreatmentGroup.style.display = 'none';
        } else if (selectedTreatment === 'custom') {
            treatmentDescription.style.display = 'none';
            customTreatmentGroup.style.display = 'block';
        } else {
            treatmentDescription.style.display = 'none';
            customTreatmentGroup.style.display = 'none';
        }
    });

    // Function to toggle treatment-specific fields
    function toggleTreatmentFields(logType) {
        const treatmentGroup = document.getElementById('treatmentGroup');
        const customTreatmentGroup = document.getElementById('customTreatmentGroup');
        const treatmentDescription = document.getElementById('treatmentDescription');
        const treatmentSelect = document.getElementById('treatmentSelect');

        if (logType === 'Treatment') {
            treatmentGroup.style.display = 'block';
            
            // Re-populate and reset treatment dropdown
            treatmentSelect.innerHTML = '<option value="">Select a treatment...</option>';
            for (const treatment in TREATMENTS) {
                const option = document.createElement('option');
                option.value = treatment;
                option.textContent = treatment;
                treatmentSelect.appendChild(option);
            }
            const customOption = document.createElement('option');
            customOption.value = 'custom';
            customOption.textContent = 'Custom Treatment';
            treatmentSelect.appendChild(customOption);
            
            // Set initial visibility correctly for TREATMENT log type
            customTreatmentGroup.style.display = 'none';
            treatmentDescription.style.display = 'none';

        } else {
            treatmentGroup.style.display = 'none';
            customTreatmentGroup.style.display = 'none';
            treatmentDescription.style.display = 'none';
        }
    }
    // Function to reset treatment fields
    function resetTreatmentFields() {
        document.getElementById('treatmentSelect').value = '';
        document.getElementById('customTreatment').value = '';
        document.getElementById('treatmentDescription').style.display = 'none';
        document.getElementById('customTreatmentGroup').style.display = 'none';
    }

    // Function to show event form
    // function showEventForm(action, event = null, selectionInfo = null) {
    //     modalTitle.textContent = action === 'create' ? 'Create Log' : 'Edit Log';
    //     deleteBtn.style.display = action === 'edit' ? 'block' : 'none';

    //     document.getElementById('eventId').value = '';
    //     document.getElementById('eventType').value = 'Period';
    //     document.getElementById('eventDescription').value = '';

    //     if (action === 'create' && selectionInfo) {
    //         const startDate = selectionInfo.start;
    //         let endDate = selectionInfo.end || selectionInfo.start;

    //         // FullCalendar's selectionInfo.end is exclusive (+1 day).
    //         // Subtract one day to show the actual end day in the form.
    //         if (endDate && !isSameDay(startDate, endDate)) {
    //             endDate = new Date(endDate);
    //             endDate.setDate(endDate.getDate() - 1);
    //         } else {
    //             endDate = startDate;
    //         }

    //         document.getElementById('eventStartDate').value = formatDate(startDate);
    //         document.getElementById('eventEndDate').value = formatDate(endDate);

    //     } else if (action === 'edit' && event) {
    //         document.getElementById('eventId').value = event.id;
    //         document.getElementById('eventType').value = event.extendedProps.type || 'Period';
    //         document.getElementById('eventDescription').value = event.extendedProps.description || '';
    //         const treatmentName = event.extendedProps.treatment_name || '';
    //         if (treatmentName) { // Check if it's a predefined treatment
    //             if (TREATMENTS[treatmentName]) {
    //                 treatmentSelect.value = treatmentName;
    //                 treatmentDescription.textContent = TREATMENTS[treatmentName].description;
    //                 treatmentDescription.style.display = 'block';
    //                 customTreatmentGroup.style.display = 'none';
    //             } else {
    //                 // It's a custom treatment
    //                 treatmentSelect.value = 'custom';
    //                 customTreatment.value = treatmentName;
    //                 customTreatmentGroup.style.display = 'block';
    //                 treatmentDescription.style.display = 'none';
    //             }
    //         }
    //         let displayEndDate = event.end ? new Date(event.end) : new Date(event.start);
    //         let displayStartDate = new Date(event.start);

    //         // Assuming all logs are "all-day" events where end date is exclusive (end date is stored +1 day)
    //         // Only subtract 1 day if it's a multi-day event or if start/end are different
    //         if (!isSameDay(displayStartDate, displayEndDate)) {
    //             displayEndDate.setDate(displayEndDate.getDate() - 1);
    //         } else {
    //             // If it's a single-day event, use the start date as the end date
    //             displayEndDate = displayStartDate;
    //         }

    //         document.getElementById('eventStartDate').value = formatDate(displayStartDate);
    //         document.getElementById('eventEndDate').value = formatDate(displayEndDate);
    //     }

    //     modal.style.display = 'flex';
    // }

// Function to show event form
function showEventForm(action, event = null, selectionInfo = null) {
    modalTitle.textContent = action === 'create' ? 'Create Log' : 'Edit Log';
    deleteBtn.style.display = action === 'edit' ? 'block' : 'none';

    document.getElementById('eventId').value = '';
    document.getElementById('eventType').value = 'Period';
    document.getElementById('eventDescription').value = '';
    
    // Reset treatment fields
    resetTreatmentFields();

    if (action === 'create' && selectionInfo) {
        const startDate = selectionInfo.start;
        let endDate = selectionInfo.end || selectionInfo.start;

        if (endDate && !isSameDay(startDate, endDate)) {
            endDate = new Date(endDate);
            endDate.setDate(endDate.getDate() - 1);
        } else {
            endDate = startDate;
        }

        document.getElementById('eventStartDate').value = formatDate(startDate);
        document.getElementById('eventEndDate').value = formatDate(endDate);

    } else if (action === 'edit' && event) {
        document.getElementById('eventId').value = event.id;
        const eventType = event.extendedProps.type || 'Period';
        document.getElementById('eventType').value = eventType;
        document.getElementById('eventDescription').value = event.extendedProps.description || '';

        // ⚠️ EDITING LOGIC: Subtract one day from the stored end date
        let displayEndDate = event.end ? new Date(event.end) : new Date(event.start);
        let displayStartDate = new Date(event.start);

        if (!isSameDay(displayStartDate, displayEndDate)) {
            displayEndDate.setDate(displayEndDate.getDate() - 1);
        } else {
            displayEndDate = displayStartDate;
        }

        document.getElementById('eventStartDate').value = formatDate(displayStartDate);
        document.getElementById('eventEndDate').value = formatDate(displayEndDate);
    }

    // Show treatment fields if editing a treatment log
    const eventType = action === 'edit' && event ? event.extendedProps.type : 'Period';
    toggleTreatmentFields(eventType);
    
    // Pre-populate treatment fields if editing a treatment log
    if (action === 'edit' && event && event.extendedProps.type === 'Treatment') {
        const treatmentName = event.extendedProps.treatment_name || '';
        const treatmentSelect = document.getElementById('treatmentSelect');
        const customTreatment = document.getElementById('customTreatment');
        const treatmentDescription = document.getElementById('treatmentDescription');
        const customTreatmentGroup = document.getElementById('customTreatmentGroup');
        
        console.log("Editing treatment log:", treatmentName); // Debug log
        
        if (treatmentName) {
            // Check if it's a predefined treatment
            if (TREATMENTS[treatmentName]) {
                treatmentSelect.value = treatmentName;
                treatmentDescription.textContent = TREATMENTS[treatmentName].description;
                treatmentDescription.style.display = 'block';
                customTreatmentGroup.style.display = 'none';
            } else {
                // It's a custom treatment
                treatmentSelect.value = 'custom';
                customTreatment.value = treatmentName;
                customTreatmentGroup.style.display = 'block';
                treatmentDescription.style.display = 'none';
            }
        }
    }

    modal.style.display = 'flex';
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
        let description = document.getElementById('eventDescription').value;
        const startDateInput = document.getElementById('eventStartDate').value;
        const endDateInput = document.getElementById('eventEndDate').value;

        let treatmentName = '';
        // Handle treatment-specific description
        if (type === 'Treatment') {
            const treatmentSelect = document.getElementById('treatmentSelect').value;
            const customTreatment = document.getElementById('customTreatment').value;

            if (treatmentSelect === 'custom' && customTreatment.trim()) {
                treatmentName = customTreatment.trim();
            } else if (treatmentSelect && treatmentSelect !== 'custom') {
                treatmentName = treatmentSelect;
            } else {
                alert('Please select or enter a treatment name');
                return;
            }
        }

        // Convert to Date objects
        const startDateObj = new Date(startDateInput);
        let endDateObj = new Date(endDateInput);

        
        // This makes the end date exclusive, following the FullCalendar/database convention.
        // This is done because all your events are essentially 'allDay' logs.
        if (!isSameDay(startDateObj, endDateObj)) {
            endDateObj.setDate(endDateObj.getDate() + 1);
        } else {
             // For single-day events, the end date must also be +1 day to span the whole day.
             endDateObj.setDate(endDateObj.getDate() + 1);
        }


        const formData = {
            type: type,
            description: description,
            treatment_name: treatmentName,
            start_date: startDateObj.toISOString(),
            end_date: endDateObj.toISOString() // This is the adjusted (+1 day) end date
        };
        console.log("Saving event with data:", formData);
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
                resetTreatmentFields();
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
                resetTreatmentFields();
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
        try {
            const startDateObj = new Date(event.start);
            let endDateObj;

            // FullCalendar already calculates the exclusive end date (+1 day) when dragging/resizing.
            // We just need to ensure the end date is properly defined.
            if (event.end) {
                endDateObj = new Date(event.end);
            } else {
                // If FullCalendar didn't provide an end date (e.g., single-day drag), 
                // we set the end date to start date + 1 day for the exclusive convention.
                endDateObj = new Date(startDateObj);
                endDateObj.setDate(endDateObj.getDate() + 1);
            }

            console.log("Updating event dates:");
            console.log("Start:", startDateObj);
            console.log("End:", endDateObj);
            console.log("Event ID:", event.id);

            const formData = {
                type: event.extendedProps.type,
                treatment_name: event.extendedProps.treatment_name || '',
                description: event.extendedProps.description || '',
                start_date: startDateObj.toISOString(),
                end_date: endDateObj.toISOString() // Use the date provided by FullCalendar (which is +1 day)
            };

            fetch('/logs/' + event.id, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error('Network response was not ok');
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('Event updated successfully');
                    // Optional: Refresh events to ensure UI consistency
                    // The event will visually update instantly because FullCalendar handles it, 
                    // but a refetch ensures the latest data is present.
                    setTimeout(() => calendar.refetchEvents(), 100);
                } else {
                    throw new Error(data.error || 'Unknown server error');
                }
            })
            .catch(error => {
                console.error('Error updating event:', error);
                alert('Failed to update log: ' + error.message);
                event.revert();
            });

        } catch (error) {
            console.error('Error in updateEvent:', error);
            alert('Error updating event: ' + error.message);
            event.revert();
        }
    }

    // Helper function to check if two dates are the same day
    function isSameDay(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }
});