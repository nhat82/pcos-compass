// script.js
const calendar = document.getElementById("calendar");
const modal = document.getElementById("eventModal");
const closeModal = document.getElementById("closeModal");
const eventForm = document.getElementById("eventForm");
const deleteButton = document.getElementById("deleteButton");
const modalTitle = document.getElementById("modalTitle");

// Event details elements
const eventDetails = document.getElementById("eventDetails");
const closeDetails = document.getElementById("closeDetails");
const editButton = document.getElementById("editButton");
const deleteDetailsButton = document.getElementById("deleteDetailsButton");

let selectedDate = null;
let selectedEvent = null;

function renderCalendar() {
  calendar.innerHTML = "";
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();

  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  // Empty cells before first day
  for (let i = 0; i < firstDay; i++) {
    const emptyCell = document.createElement("div");
    calendar.appendChild(emptyCell);
  }

  // Days of month
  for (let d = 1; d <= daysInMonth; d++) {
    const dayCell = document.createElement("div");
    dayCell.className = "day";
    dayCell.textContent = d;
    dayCell.addEventListener("click", () => openModal(year, month, d));
    calendar.appendChild(dayCell);
  }

  // Fetch and display events
  fetch("/events/")
    .then(res => res.json())
    .then(data => {
      // Sort events by duration (longest first)
      const sortedEvents = data.events.sort((a, b) => {
        const durationA = new Date(a.end_date) - new Date(a.start_date);
        const durationB = new Date(b.end_date) - new Date(b.start_date);
        return durationB - durationA; // Descending order
      });

      // Create a grid to track event positions for each day
      const dayGrid = Array(daysInMonth).fill().map(() => []);

      sortedEvents.forEach(event => {
        const startDate = new Date(event.start_date);
        const endDate = new Date(event.end_date);
        
        const currentMonthStart = new Date(year, month, 1);
        const currentMonthEnd = new Date(year, month + 1, 0);
        
        const displayStart = startDate < currentMonthStart ? currentMonthStart : startDate;
        const displayEnd = endDate > currentMonthEnd ? currentMonthEnd : endDate;
        
        if (displayStart <= currentMonthEnd && displayEnd >= currentMonthStart) {
          const startDay = displayStart.getDate();
          const endDay = displayEnd.getDate();
          
          // Find the first available row for this event
          let row = 0;
          while (true) {
            let conflict = false;
            for (let d = startDay; d <= endDay; d++) {
              if (dayGrid[d-1] && dayGrid[d-1][row]) {
                conflict = true;
                break;
              }
            }
            if (!conflict) break;
            row++;
          }
          
          // Reserve the row and create event elements
          for (let d = startDay; d <= endDay; d++) {
            const dayIndex = firstDay + d - 1;
            if (!dayGrid[d-1]) dayGrid[d-1] = [];
            dayGrid[d-1][row] = true; // Mark this position as occupied
            
            if (dayIndex >= 0 && dayIndex < calendar.children.length) {
              const cell = calendar.children[dayIndex];
              const div = document.createElement("div");
              div.className = "event";
              div.style.backgroundColor = getEventColor(event.type);
              div.style.order = row; // Use CSS order to maintain vertical position
              div.dataset.type = event.type;
              // Only show description on first day or if it's a single day
              if (d === startDay || startDay === endDay) {
                div.textContent = event.description || event.type;
                if (startDay !== endDay) {
                  div.textContent += " →";
                }
              } else {
                div.textContent = "→";
              }
              
              div.addEventListener("click", (e) => {
                e.stopPropagation();
                showEventDetails(event);
              });
              
              // Create a container for events if it doesn't exist
              let eventContainer = cell.querySelector('.event-container');
              if (!eventContainer) {
                eventContainer = document.createElement("div");
                eventContainer.className = 'event-container';
                cell.appendChild(eventContainer);
              }
              
              eventContainer.appendChild(div);
            }
          }
        }
      });
    });
}

function getEventColor(type) {
  const colors = {
    'PERIOD': '#ffcccc',
    'OVULATION': '#ccffcc',
    'NOTE': '#ccccff'
  };
  return colors[type] || '#e3f2fd';
}

function openModal(year, month, day, event = null) {
  selectedDate = new Date(year, month, day);
  selectedEvent = event;
  
  if (event) {
    // Editing existing event
    modalTitle.textContent = "Edit Event";
    document.getElementById("eventId").value = event.id;
    document.getElementById("type").value = event.type;
    document.getElementById("description").value = event.description || "";
    document.getElementById("startDate").value = event.start_date.split("T")[0];
    document.getElementById("endDate").value = event.end_date.split("T")[0];
    deleteButton.classList.remove("hidden");
  } else {
    // Creating new event
    modalTitle.textContent = "Create Event";
    document.getElementById("eventId").value = "";
    document.getElementById("type").value = "PERIOD";
    document.getElementById("description").value = "";
    
    // Set both start and end dates to the selected day by default
    const dateStr = selectedDate.toISOString().split("T")[0];
    document.getElementById("startDate").value = dateStr;
    document.getElementById("endDate").value = dateStr;
    
    deleteButton.classList.add("hidden");
  }
  
  modal.classList.remove("hidden");
}

function showEventDetails(event) {
  document.getElementById("eventDetailsTitle").textContent = event.type;
  document.getElementById("eventDetailsType").textContent = `Type: ${event.type}`;
  document.getElementById("eventDetailsDescription").textContent = `Description: ${event.description || "None"}`;
  
  const startDate = new Date(event.start_date);
  const endDate = new Date(event.end_date);
  
  // Format dates nicely
  const dateFormatOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const startDateStr = startDate.toLocaleDateString(undefined, dateFormatOptions);
  const endDateStr = endDate.toLocaleDateString(undefined, dateFormatOptions);
  
  document.getElementById("eventDetailsDates").textContent = 
    `From: ${startDateStr}\nTo: ${endDateStr}`;
  
  // Store event ID in the buttons
  editButton.dataset.eventId = event.id;
  deleteDetailsButton.dataset.eventId = event.id;
  
  eventDetails.classList.remove("hidden");
}

closeModal.addEventListener("click", () => {
  modal.classList.add("hidden");
  selectedEvent = null;
});

closeDetails.addEventListener("click", () => {
  eventDetails.classList.add("hidden");
});

deleteButton.addEventListener("click", async () => {
  if (selectedEvent && confirm("Are you sure you want to delete this event?")) {
    await fetch(`/events/${selectedEvent.id}`, {
      method: "DELETE"
    });
    modal.classList.add("hidden");
    renderCalendar();
  }
});

editButton.addEventListener("click", async () => {
  const eventId = editButton.dataset.eventId;
  const response = await fetch(`/events/${eventId}`);
  const event = await response.json();
  eventDetails.classList.add("hidden");
  
  const eventDate = new Date(event.start_date);
  openModal(
    eventDate.getFullYear(),
    eventDate.getMonth(),
    eventDate.getDate(),
    event
  );
});

deleteDetailsButton.addEventListener("click", async () => {
  const eventId = deleteDetailsButton.dataset.eventId;
  if (confirm("Are you sure you want to delete this event?")) {
    await fetch(`/events/${eventId}`, {
      method: "DELETE"
    });
    eventDetails.classList.add("hidden");
    renderCalendar();
  }
});

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
  
  await fetch(url, {
    method: method,
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });
  
  modal.classList.add("hidden");
  renderCalendar();
});

// Initial render
renderCalendar();