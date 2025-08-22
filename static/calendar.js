// script.js
document.addEventListener('DOMContentLoaded', function() {
  const calendarEl = document.getElementById('calendar');
  const modal = document.getElementById('eventModal');
  const closeModal = document.getElementById('closeModal');
  const eventForm = document.getElementById('eventForm');
  const deleteButton = document.getElementById('deleteButton');
  const modalTitle = document.getElementById('modalTitle');

  let currentEvent = null;
  let calendar = null;
  let selectedRange = null;

  // Initialize FullCalendar
  function initCalendar() {
    calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth'
      },
      events: '/events/',
      selectable: true, // Enable selection
      selectMirror: true,
      select: function(info) {
        selectedRange = info;
        showEventModalForSelection(info.start, info.end);
      },
      eventClick: function(info) {
        info.jsEvent.preventDefault();
        console.log("Event clicked:", info.event);
        console.log("Event ID:", info.event.id);
        console.log("Event extendedProps:", info.event.extendedProps);
        showEventModal(info.event, true);
      },
      eventContent: function(arg) {
        // Custom event rendering
        const event = arg.event;
        const title = event.title || event.extendedProps.type;
        const backgroundColor = getEventColor(event.extendedProps.type);
        
        return {
          html: `<div style="background-color: ${backgroundColor}; padding: 2px; border-radius: 3px; margin: 1px;"> ${title}</div>`
        };
      },
      editable: true, // Enable drag and drop
      eventDrop: function(info) {
        // Handle event drag and drop
        updateEventViaAPI(info.event);
      },
      eventResize: function(info) {
        // Handle event resize
        updateEventViaAPI(info.event);
      }
    });

    calendar.render();
  }

  // Get event color based on type
  function getEventColor(type) {
    const colors = {
      'PERIOD': '#9c0000ff',
      'OVULATION': '#07a5c4ff',
      'NOTE': '#7373baff'
    };
    return colors[type];
  }

  // Show modal for selection (drag-to-create)
 function showEventModalForSelection(start, end) {
    modalTitle.textContent = "Create Event";
    document.getElementById("eventId").value = "";
    document.getElementById("type").value = "PERIOD";
    document.getElementById("description").value = "";
    
    // Correct for FullCalendar's non-inclusive end date
    const correctedEndDate = new Date(end);
    correctedEndDate.setDate(correctedEndDate.getDate() - 1);
    
    document.getElementById("startDate").value = formatDateTimeLocal(start);
    document.getElementById("endDate").value = formatDateTimeLocal(correctedEndDate);
    
    deleteButton.classList.add("hidden");
    
    modal.classList.remove("hidden");
  }

  // Show modal for existing event
  function showEventModal(event = null, isEdit = false) {
    currentEvent = event;
    
    if (isEdit && event) {
      modalTitle.textContent = "Edit Event";
      document.getElementById("eventId").value = event.id;
      document.getElementById("type").value = event.extendedProps.type;
      document.getElementById("description").value = event.extendedProps.description || "";
      document.getElementById("startDate").value = formatDateTimeLocal(event.start);
      document.getElementById("endDate").value = event.end ? formatDateTimeLocal(event.end) : formatDateTimeLocal(event.start);
      deleteButton.classList.remove("hidden");
    }
    
    modal.classList.remove("hidden");
  }

  // Format date for datetime-local input
  function formatDateTimeLocal(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toISOString().slice(0, 16);
  }

  // Close modal
  closeModal.addEventListener("click", () => {
    modal.classList.add("hidden");
    currentEvent = null;
    if (selectedRange) {
      selectedRange.jsEvent.preventDefault();
      selectedRange = null;
    }
  });

  // Handle form submission
  eventForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const eventId = document.getElementById("eventId").value;
    const method = eventId ? "PUT" : "POST";
    const url = eventId ? `/events/${eventId}` : "/events/";
    
    const data = {
      type: document.getElementById("type").value,
      description: document.getElementById("description").value,
      start_date: document.getElementById("startDate").value,
      end_date: document.getElementById("endDate").value
    };
    
    try {
      const response = await fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });
      
      if (response.ok) {
        modal.classList.add("hidden");
        calendar.refetchEvents(); // Refresh calendar events
        if (selectedRange) {
          selectedRange.jsEvent.preventDefault();
          selectedRange = null;
        }
      } else {
        console.error("Error:", await response.json());
      }
    } catch (error) {
      console.error("Request failed:", error);
    }
  });

  // Handle delete

  deleteButton.addEventListener("click", async () => {
    if (currentEvent && confirm("Are you sure you want to delete this event?")) {
      try {
        console.log("Deleting event ID:", currentEvent.id);
        
        const response = await fetch(`/events/${currentEvent.id}`, {
          method: "DELETE"
        });
        
        console.log("Delete response status:", response.status);
        
        if (response.ok) {
          console.log("Delete successful");
          modal.classList.add("hidden");
          calendar.refetchEvents(); // Refresh calendar events
        } else {
          const errorData = await response.json();
          console.error("Delete failed:", errorData);
          alert("Delete failed: " + (errorData.error || "Unknown error"));
        }
      } catch (error) {
        console.error("Delete request failed:", error);
        alert("Delete request failed: " + error.message);
      }
    }
  });

  // Update event via API (for drag and drop)
  async function updateEventViaAPI(event) {
    const data = {
      type: event.extendedProps.type,
      description: event.extendedProps.description || "",
      start_date: event.start ? event.start.toISOString() : new Date().toISOString(),
      end_date: event.end ? event.end.toISOString() : event.start.toISOString()
    };
    
    try {
      const response = await fetch(`/events/${event.id}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        console.error("Update failed:", await response.json());
        // Revert the event position on error
        calendar.refetchEvents();
      }
    } catch (error) {
      console.error("Update request failed:", error);
      calendar.refetchEvents();
    }
  }

  // Initialize the calendar
  initCalendar();
  
});