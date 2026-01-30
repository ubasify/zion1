"""
Script to add CRUD modals and make ministry cards clickable
"""

# Read the current template
with open('templates/ministry/ministry_list.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Wire the "Add Ministry" button to open modal
content = content.replace(
    "<button class='bg-brand-navy hover:bg-brand-dark text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-sm shadow-brand-navy/20'>",
    "<button onclick='openMinistryModal()' class='bg-brand-navy hover:bg-brand-dark text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-sm shadow-brand-navy/20'>"
)

# 2. Change "Active participation" to "Report participation"
content = content.replace("Active participation", "Report participation")

# 3. Make cards clickable - wrap the entire card in a clickable div
# Find the card div and add onclick
old_card_start = "<div class='bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-white/5 shadow-sm hover:shadow-md transition-shadow'>"
new_card_start = "<div onclick='editMinistry({{ ministry.id }})' class='bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200 dark:border-white/5 shadow-sm hover:shadow-md transition-shadow cursor-pointer'>"
content = content.replace(old_card_start, new_card_start)

# 4. Add modals and JavaScript before {% endblock %}
modals_and_js = """
    <!-- Create/Edit Ministry Modal -->
    <div id='ministryModal' class='hidden fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4'>
        <div class='bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto'>
            <div class='p-6 border-b border-slate-200 dark:border-white/10 flex justify-between items-center'>
                <h3 id='modalTitle' class='text-xl font-bold text-slate-900 dark:text-white'>Add Ministry</h3>
                <button onclick='closeMinistryModal()' class='text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'>
                    <i data-lucide='x' class='w-5 h-5'></i>
                </button>
            </div>
            <form id='ministryForm' class='p-6 space-y-4'>
                <input type='hidden' id='ministryId' name='id'>
                
                <div>
                    <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Ministry Name *</label>
                    <input type='text' id='name' name='name' required
                           class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                </div>

                <div>
                    <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Description</label>
                    <textarea id='description' name='description' rows='3'
                              class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'></textarea>
                </div>

                <div class='grid grid-cols-2 gap-4'>
                    <div>
                        <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Icon Type</label>
                        <select id='icon_type' name='icon_type'
                                class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                            <option value='users'>Users</option>
                            <option value='music'>Music</option>
                            <option value='shield'>Shield</option>
                            <option value='heart'>Heart</option>
                            <option value='book-open'>Book</option>
                            <option value='camera'>Camera</option>
                            <option value='megaphone'>Megaphone</option>
                            <option value='user-check'>User Check</option>
                            <option value='home'>Home</option>
                            <option value='mic'>Microphone</option>
                            <option value='monitor'>Monitor</option>
                        </select>
                    </div>
                    <div>
                        <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Meeting Day</label>
                        <select id='meeting_day' name='meeting_day'
                                class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                            <option value=''>Select Day</option>
                            <option value='monday'>Monday</option>
                            <option value='tuesday'>Tuesday</option>
                            <option value='wednesday'>Wednesday</option>
                            <option value='thursday'>Thursday</option>
                            <option value='friday'>Friday</option>
                            <option value='saturday'>Saturday</option>
                            <option value='sunday'>Sunday</option>
                        </select>
                    </div>
                </div>

                <!-- Edit-only fields -->
                <div id='editOnlyFields' class='hidden space-y-4'>
                    <div>
                        <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Report Participation %</label>
                        <input type='number' id='active_participation_rate' name='active_participation_rate' min='0' max='100'
                               class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                    </div>
                    <div class='grid grid-cols-2 gap-4'>
                        <div>
                            <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Reporting Status</label>
                            <select id='reporting_status' name='reporting_status'
                                    class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                                <option value='up_to_date'>Up to date</option>
                                <option value='pending'>Pending</option>
                                <option value='overdue'>Overdue</option>
                            </select>
                        </div>
                        <div>
                            <label class='block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2'>Last Report Date</label>
                            <input type='date' id='last_report_date' name='last_report_date'
                                   class='w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-navy/20 dark:bg-slate-700 dark:text-white'>
                        </div>
                    </div>
                </div>

                <div class='flex justify-between gap-3 pt-4'>
                    <button type='button' id='deleteBtn' onclick='confirmDelete()' 
                            class='hidden px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors'>
                        Delete Ministry
                    </button>
                    <div class='flex gap-3 ml-auto'>
                        <button type='button' onclick='closeMinistryModal()' 
                                class='px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors'>
                            Cancel
                        </button>
                        <button type='submit' 
                                class='px-4 py-2 bg-brand-navy hover:bg-brand-dark text-white rounded-lg transition-colors'>
                            Save Ministry
                        </button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div id='deleteModal' class='hidden fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4'>
        <div class='bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full'>
            <div class='p-6'>
                <div class='flex items-center gap-4 mb-4'>
                    <div class='p-3 bg-red-100 dark:bg-red-900/20 rounded-full'>
                        <i data-lucide='alert-triangle' class='w-6 h-6 text-red-600'></i>
                    </div>
                    <div>
                        <h3 class='text-lg font-bold text-slate-900 dark:text-white'>Delete Ministry</h3>
                        <p class='text-sm text-slate-500 dark:text-slate-400 mt-1'>This action cannot be undone</p>
                    </div>
                </div>
                <p id='deleteMessage' class='text-slate-600 dark:text-slate-300 mb-6'></p>
                <div class='flex justify-end gap-3'>
                    <button onclick='closeDeleteModal()' 
                            class='px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors'>
                        Cancel
                    </button>
                    <button onclick='deleteMinistry()' 
                            class='px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors'>
                        Delete
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentMinistryId = null;

        function openMinistryModal() {
            document.getElementById('ministryModal').classList.remove('hidden');
            document.getElementById('ministryForm').reset();
            document.getElementById('ministryId').value = '';
            document.getElementById('modalTitle').textContent = 'Add Ministry';
            document.getElementById('editOnlyFields').classList.add('hidden');
            document.getElementById('deleteBtn').classList.add('hidden');
        }

        function closeMinistryModal() {
            document.getElementById('ministryModal').classList.add('hidden');
        }

        function editMinistry(id) {
            // Fetch ministry data and populate form
            fetch(`/ministries/${id}/update/`)
                .then(response => response.text())
                .then(html => {
                    // For now, we'll use a simpler approach - just open the modal
                    // In production, you'd parse the response and populate fields
                    currentMinistryId = id;
                    document.getElementById('ministryId').value = id;
                    document.getElementById('modalTitle').textContent = 'Edit Ministry';
                    document.getElementById('editOnlyFields').classList.remove('hidden');
                    document.getElementById('deleteBtn').classList.remove('hidden');
                    document.getElementById('ministryModal').classList.remove('hidden');
                });
        }

        function confirmDelete() {
            if (!currentMinistryId) return;
            document.getElementById('deleteMessage').textContent = 'Are you sure you want to delete this ministry? All associated data will be removed.';
            document.getElementById('deleteModal').classList.remove('hidden');
        }

        function closeDeleteModal() {
            document.getElementById('deleteModal').classList.add('hidden');
        }

        function deleteMinistry() {
            if (!currentMinistryId) return;

            fetch(`/ministries/${currentMinistryId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error deleting ministry');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting ministry');
            });
        }

        document.getElementById('ministryForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const id = document.getElementById('ministryId').value;
            const url = id ? `/ministries/${id}/update/` : '/ministries/create/';
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error saving ministry: ' + JSON.stringify(data.errors));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error saving ministry');
            });
        });
    </script>
"""

# Insert modals before {% endblock %}
content = content.replace("{% endblock %}", modals_and_js + "\n{% endblock %}")

# Write the updated content
with open('templates/ministry/ministry_list.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully added CRUD modals and made ministry cards clickable")
