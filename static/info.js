// This script handles dynamic subject fields and average marks calculation for updating the form based on the selected education level.
// It also manages the visibility of the CPI/CGPA block based on the education level.
const streamTitles = {
    school: "🎓 School Subjects (Class 1–12)",
    bsc: "🎓 College Subjects (B.Sc. Science)",
    engineering: "🎓 College Subjects (Engineering)",
    commerce: "🎓 College Subjects (Commerce)",
    Arts: "🎓 College Subjects (Arts)",
    Doctor: "🎓 College Subjects (Doctors)"
};

function showSubjectsSection(val) {
    let section = document.getElementById('dynamic-subjects-section');
    let title = document.getElementById('subject-section-title');
    let subjectsList = document.getElementById('subjects-list');
    let cpiBlock = document.getElementById('cpi-cgpa-block');
    if (val) {
        section.style.display = 'block';
        title.textContent = streamTitles[val] || "Subjects";
        // Only add a blank subject row if there are no pre-filled subjects
        if (!subjectsList.children.length) {
            addSubjectField();
        }
        calcDynamicAvg();
        // Show CPI/CGPA for college streams
        if (val === 'school') {
            cpiBlock.style.display = 'none';
        } else {
            cpiBlock.style.display = 'block';
        }
    } else {
        section.style.display = 'none';
        subjectsList.innerHTML = '';
        title.textContent = '';
        document.getElementById('dynamic-avg-marks').value = '';
        cpiBlock.style.display = 'none';
    }
}

document.getElementById('education_level').addEventListener('change', function () {
    showSubjectsSection(this.value);
    toggleCpiCgpaBlock();
});

// Add subject field dynamically
function addSubjectField() {
    const subjectsList = document.getElementById('subjects-list');
    const div = document.createElement('div');
    div.className = 'subject-row';
    div.style.marginBottom = '8px';
    div.innerHTML = `
        <input type="text" name="subject_names[]" placeholder="Subject Name" required style="width:180px; margin-right:8px;">
        <input type="number" name="subject_marks[]" min="0" max="100" placeholder="Marks" required style="width:100px;" class="dynamic-marks">
        <button type="button" class="remove-subject-btn" style="margin-left:8px;">❌</button>
    `;
    subjectsList.appendChild(div);

    // Attach remove event to the new button
    attachRemoveEvents();

    // Recalculate average on input
    div.querySelector('input[type="number"]').addEventListener('input', calcDynamicAvg);
}

// Attach remove event to all remove buttons (for pre-filled and new)
function attachRemoveEvents() {
    document.querySelectorAll('.remove-subject-btn').forEach(function(btn) {
        btn.onclick = function () {
            btn.parentElement.remove();
            calcDynamicAvg();
        };
    });
}

// Add subject on button click
document.getElementById('add-subject-btn').onclick = addSubjectField;

// Calculate average marks dynamically
function calcDynamicAvg() {
    let marksInputs = document.querySelectorAll('.dynamic-marks');
    let values = Array.from(marksInputs)
        .map(input => input.value)
        .filter(val => val !== "")
        .map(Number);
    let avg = values.length ? (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2) : '';
    document.getElementById('dynamic-avg-marks').value = avg;
}

// Show/hide CPI/CGPA field based on education level
function toggleCpiCgpaBlock() {
    var edu = document.getElementById('education_level');
    var cpiBlock = document.getElementById('cpi-cgpa-block');
    if (!edu || !cpiBlock) return;
    if (edu.value === 'school' || edu.value === '') {
        cpiBlock.style.display = 'none';
    } else {
        cpiBlock.style.display = 'block';
    }
}

// On page load: attach events to pre-filled fields and remove buttons
// Run on page load
window.onload = function () {
    let educationLevel = document.getElementById('education_level').value;
    showSubjectsSection(educationLevel);

    // Attach input event to all existing .dynamic-marks fields
    document.querySelectorAll('.dynamic-marks').forEach(function(input) {
        input.addEventListener('input', calcDynamicAvg);
    });

    // Attach remove events to all pre-filled remove buttons
    attachRemoveEvents();

    // Also recalculate average on load
    calcDynamicAvg();

    // Show/hide CPI/CGPA block
    toggleCpiCgpaBlock();
};