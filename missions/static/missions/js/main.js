

console.log('🌟 Inline JavaScript loaded!');

class JediMissionBoard {
    constructor() {
        this.tasks = [];
        this.taskIdCounter = 0;
        this.isLoading = false;

        console.log('🌟 JediMissionBoard constructor called');
        console.log('📄 Document ready state:', document.readyState);

        if (document.readyState === 'loading') {
            console.log('⏳ DOM still loading, waiting for DOMContentLoaded...');
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            console.log('✅ DOM already loaded, initializing immediately');
            this.init();
        }
    }

    init() {
        console.log('🚀 Initializing Jedi Mission Board...');
        this.bindEvents();

        setTimeout(() => {
            this.loadTasks();
        }, 500);
    }

    showLoading() {
        console.log('📡 Showing loading indicator...');
        const loadingIndicator = document.getElementById('loading-indicator');
        const taskContainer = document.querySelector('.task-container');

        if (loadingIndicator) {
            this.isLoading = true;
            loadingIndicator.style.display = 'flex';
            console.log('✅ Loading indicator shown');
        }

        if (taskContainer) {
            taskContainer.style.display = 'none';
            console.log('✅ Task container hidden');
        }

        this.setButtonsDisabled(true);
    }

    hideLoading() {
        console.log('🔄 Hiding loading indicator...');
        const loadingIndicator = document.getElementById('loading-indicator');
        const taskContainer = document.querySelector('.task-container');

        if (loadingIndicator) {
            this.isLoading = false;
            loadingIndicator.style.display = 'none';
            console.log('✅ Loading indicator hidden');
        }

        if (taskContainer) {
            taskContainer.style.display = 'block';
            console.log('✅ Task container shown');
        }

        this.setButtonsDisabled(false);
    }

    setButtonsDisabled(disabled) {
        const refreshBtn = document.getElementById('refresh-tasks');
        const addTaskBtn = document.getElementById('add-task');

        if (refreshBtn) {
            refreshBtn.disabled = disabled;
            if (disabled) {
                refreshBtn.textContent = '⏳ Loading...';
                refreshBtn.classList.add('loading');
            } else {
                refreshBtn.textContent = '🚀 Generate New Missions';
                refreshBtn.classList.remove('loading');
            }
        }

        if (addTaskBtn) {
            addTaskBtn.disabled = disabled;
        }
    }

    bindEvents() {
        console.log('🔗 Binding events...');

        const refreshBtn = document.getElementById('refresh-tasks');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                if (!this.isLoading) {
                    console.log('🔄 Refresh button clicked');
                    this.loadTasks();
                }
            });
        }

        const addTaskBtn = document.getElementById('add-task');
        const modal = document.getElementById('add-task-modal');
        const saveTaskBtn = document.getElementById('save-task');
        const cancelTaskBtn = document.getElementById('cancel-task');
        const newTaskInput = document.getElementById('new-task-input');

        if (addTaskBtn && modal) {
            addTaskBtn.addEventListener('click', () => {
                if (!this.isLoading) {
                    modal.style.display = 'flex';
                    newTaskInput.focus();
                }
            });
        }

        if (saveTaskBtn && newTaskInput) {
            saveTaskBtn.addEventListener('click', () => {
                const taskText = newTaskInput.value.trim();
                if (taskText) {
                    this.addCustomTask(taskText);
                    newTaskInput.value = '';
                    modal.style.display = 'none';
                }
            });
        }

        if (cancelTaskBtn) {
            cancelTaskBtn.addEventListener('click', () => {
                modal.style.display = 'none';
                newTaskInput.value = '';
            });
        }

        if (newTaskInput) {
            newTaskInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    saveTaskBtn.click();
                }
            });
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                    newTaskInput.value = '';
                }
            });
        }
    }

    async loadTasks() {
        console.log('📥 Starting loadTasks()...');
        this.showLoading();

        try {
            console.log('🌐 Making fetch request to /api/tasks/...');
            const response = await fetch('/api/tasks/');

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('📊 API Response:', data);

            if (data.tasks && Array.isArray(data.tasks) && data.tasks.length > 0) {
                this.tasks = data.tasks.map((task, index) => ({
                    id: index,
                    text: task,
                    completed: false,
                    isCustom: false
                }));
                this.taskIdCounter = this.tasks.length;
                console.log(`✅ Loaded ${this.tasks.length} tasks from API`);
            } else {
                console.warn('⚠️ API returned empty tasks, using fallback');
                this.showFallbackTasks();
            }
        } catch (error) {
            console.error('❌ Error loading tasks:', error);
            this.showFallbackTasks();
        }

        setTimeout(() => {
            console.log('🎬 Hiding loading and rendering tasks');
            this.hideLoading();
            this.renderTasks();
            this.updateProgress();
        }, 1500);
    }

    showFallbackTasks() {
        console.log('🔄 Loading fallback tasks...');
        this.tasks = [
            { id: 0, text: "Train with Master Yoda on Dagobah", completed: false, isCustom: false },
            { id: 1, text: "Deliver secret plans to the Rebel Alliance", completed: false, isCustom: false },
            { id: 2, text: "Scout the Death Star for weaknesses", completed: false, isCustom: false },
            { id: 3, text: "Meditate on the Force", completed: false, isCustom: false },
            { id: 4, text: "Repair your lightsaber", completed: false, isCustom: false }
        ];
        this.taskIdCounter = this.tasks.length;
        console.log(`✅ Fallback tasks loaded: ${this.tasks.length} tasks`);
    }

    addCustomTask(taskText) {
        const newTask = {
            id: this.taskIdCounter++,
            text: taskText,
            completed: false,
            isCustom: true
        };
        this.tasks.push(newTask);
        this.renderTasks();
        this.updateProgress();
    }

    toggleTask(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
            task.completed = !task.completed;
            this.updateProgress();
            this.renderTasks();
        }
    }

    editTask(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
            const newText = prompt('Edit mission:', task.text);
            if (newText && newText.trim()) {
                task.text = newText.trim();
                this.renderTasks();
            }
        }
    }

    deleteTask(taskId) {
        const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
        if (taskElement) {
            taskElement.classList.add('deleting');
            setTimeout(() => {
                this.tasks = this.tasks.filter(t => t.id !== taskId);
                this.renderTasks();
                this.updateProgress();
            }, 500);
        }
    }

    renderTasks() {
        console.log('🎨 Starting renderTasks()...');
        const taskList = document.getElementById('task-list');
        const emptyState = document.getElementById('empty-state');

        if (!taskList) {
            console.error('❌ Task list element not found');
            return;
        }

        taskList.innerHTML = '';

        if (this.tasks.length === 0) {
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        if (emptyState) emptyState.style.display = 'none';

        console.log(`🎯 Rendering ${this.tasks.length} tasks...`);
        this.tasks.forEach((task, index) => {
            const li = document.createElement('li');
            li.className = `task-entry ${task.completed ? 'completed' : ''}`;
            li.setAttribute('data-task-id', task.id);
            li.style.animationDelay = `${index * 0.1}s`;

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `task-${task.id}`;
            checkbox.checked = task.completed;
            checkbox.addEventListener('change', () => this.toggleTask(task.id));

            const label = document.createElement('label');
            label.htmlFor = `task-${task.id}`;
            label.textContent = task.text;

            const actions = document.createElement('div');
            actions.className = 'task-actions';

            const editBtn = document.createElement('button');
            editBtn.className = 'task-btn edit';
            editBtn.textContent = 'Edit';
            editBtn.addEventListener('click', () => this.editTask(task.id));

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'task-btn delete';
            deleteBtn.textContent = 'Delete';
            deleteBtn.addEventListener('click', () => this.deleteTask(task.id));

            actions.appendChild(editBtn);
            actions.appendChild(deleteBtn);

            li.appendChild(checkbox);
            li.appendChild(label);
            li.appendChild(actions);
            taskList.appendChild(li);
        });

        console.log(`✅ Successfully rendered ${this.tasks.length} tasks`);
    }

    updateProgress() {
        const total = this.tasks.length;
        const completed = this.tasks.filter(task => task.completed).length;
        const percent = total > 0 ? (completed / total) * 100 : 0;

        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        const jediRank = document.getElementById('jedi-rank');

        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }

        if (progressText) {
            progressText.textContent = `Progress: ${Math.round(percent)}%`;
        }

        if (jediRank) {
            jediRank.textContent = `Rank: ${this.getJediRank(percent)}`;
        }
    }

    getJediRank(percent) {
        if (percent === 100) return 'Jedi Master';
        if (percent >= 80) return 'Jedi Knight';
        if (percent >= 60) return 'Jedi Guardian';
        if (percent >= 40) return 'Jedi Sentinel';
        if (percent >= 20) return 'Jedi Apprentice';
        return 'Padawan';
    }
}

// Initialize the application
console.log('🌟 Starting Jedi Mission Board initialization...');
const missionBoard = new JediMissionBoard();
