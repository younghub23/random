// Canvas setup
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Set canvas size
canvas.width = 600;
canvas.height = 600;

// Game variables
const gridSize = 20;
const tileCount = canvas.width / gridSize;

let snake = [{ x: 10, y: 10 }];
let velocityX = 0;
let velocityY = 0;
let food = { x: 15, y: 15 };
let score = 0;
let highScore = localStorage.getItem('cyberSnakeHighScore') || 0;
let gameLoop;
let isGameRunning = false;
let isPaused = false;
let gameSpeed = 100;

// UI Elements
const scoreElement = document.getElementById('score');
const highScoreElement = document.getElementById('highScore');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const restartBtn = document.getElementById('restartBtn');
const gameOverScreen = document.getElementById('gameOver');
const finalScoreElement = document.getElementById('finalScore');

// Initialize high score display
highScoreElement.textContent = highScore;

// Particle system for effects
let particles = [];

class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = (Math.random() - 0.5) * 4;
        this.life = 1;
        this.color = color;
        this.size = Math.random() * 3 + 2;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life -= 0.02;
        this.size *= 0.96;
    }

    draw() {
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;
        ctx.shadowBlur = 10;
        ctx.shadowColor = this.color;
        ctx.fillRect(this.x, this.y, this.size, this.size);
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;
    }
}

// Create food particles
function createFoodParticles(x, y) {
    for (let i = 0; i < 15; i++) {
        particles.push(new Particle(x * gridSize + gridSize / 2, y * gridSize + gridSize / 2, '#ff00ff'));
    }
}

// Update and draw particles
function updateParticles() {
    particles = particles.filter(p => p.life > 0);
    particles.forEach(p => {
        p.update();
        p.draw();
    });
}

// Generate random food position
function generateFood() {
    let newFood;
    let isOnSnake;

    do {
        isOnSnake = false;
        newFood = {
            x: Math.floor(Math.random() * tileCount),
            y: Math.floor(Math.random() * tileCount)
        };

        // Check if food spawned on snake
        for (let segment of snake) {
            if (segment.x === newFood.x && segment.y === newFood.y) {
                isOnSnake = true;
                break;
            }
        }
    } while (isOnSnake);

    food = newFood;
}

// Draw functions with cyberpunk effects
function drawSnake() {
    snake.forEach((segment, index) => {
        // Gradient for snake segments
        const gradient = ctx.createLinearGradient(
            segment.x * gridSize,
            segment.y * gridSize,
            segment.x * gridSize + gridSize,
            segment.y * gridSize + gridSize
        );

        if (index === 0) {
            // Head - cyan glow
            gradient.addColorStop(0, '#00ffff');
            gradient.addColorStop(1, '#00cccc');
            ctx.shadowBlur = 15;
            ctx.shadowColor = '#00ffff';
        } else {
            // Body - gradient from cyan to magenta
            const ratio = index / snake.length;
            gradient.addColorStop(0, `rgba(0, 255, 255, ${1 - ratio * 0.5})`);
            gradient.addColorStop(1, `rgba(255, 0, 255, ${1 - ratio * 0.5})`);
            ctx.shadowBlur = 10;
            ctx.shadowColor = index % 2 === 0 ? '#00ffff' : '#ff00ff';
        }

        ctx.fillStyle = gradient;
        ctx.fillRect(
            segment.x * gridSize + 1,
            segment.y * gridSize + 1,
            gridSize - 2,
            gridSize - 2
        );

        // Add border to head
        if (index === 0) {
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.strokeRect(
                segment.x * gridSize + 1,
                segment.y * gridSize + 1,
                gridSize - 2,
                gridSize - 2
            );
        }
    });

    ctx.shadowBlur = 0;
}

function drawFood() {
    // Pulsating glow effect
    const pulse = Math.sin(Date.now() / 200) * 5 + 15;

    // Outer glow
    ctx.shadowBlur = pulse;
    ctx.shadowColor = '#ff00ff';

    // Food gradient
    const gradient = ctx.createRadialGradient(
        food.x * gridSize + gridSize / 2,
        food.y * gridSize + gridSize / 2,
        0,
        food.x * gridSize + gridSize / 2,
        food.y * gridSize + gridSize / 2,
        gridSize / 2
    );
    gradient.addColorStop(0, '#ffffff');
    gradient.addColorStop(0.3, '#ff00ff');
    gradient.addColorStop(1, '#8800ff');

    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(
        food.x * gridSize + gridSize / 2,
        food.y * gridSize + gridSize / 2,
        gridSize / 2 - 2,
        0,
        Math.PI * 2
    );
    ctx.fill();

    // Inner highlight
    ctx.shadowBlur = 0;
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.beginPath();
    ctx.arc(
        food.x * gridSize + gridSize / 2 - 2,
        food.y * gridSize + gridSize / 2 - 2,
        3,
        0,
        Math.PI * 2
    );
    ctx.fill();
}

function drawGrid() {
    ctx.strokeStyle = 'rgba(0, 255, 255, 0.1)';
    ctx.lineWidth = 0.5;

    for (let i = 0; i <= tileCount; i++) {
        // Vertical lines
        ctx.beginPath();
        ctx.moveTo(i * gridSize, 0);
        ctx.lineTo(i * gridSize, canvas.height);
        ctx.stroke();

        // Horizontal lines
        ctx.beginPath();
        ctx.moveTo(0, i * gridSize);
        ctx.lineTo(canvas.width, i * gridSize);
        ctx.stroke();
    }
}

// Game logic
function moveSnake() {
    const head = { x: snake[0].x + velocityX, y: snake[0].y + velocityY };

    // Check wall collision
    if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
        gameOver();
        return;
    }

    // Check self collision
    for (let segment of snake) {
        if (segment.x === head.x && segment.y === head.y) {
            gameOver();
            return;
        }
    }

    snake.unshift(head);

    // Check food collision
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        scoreElement.textContent = score;
        createFoodParticles(food.x, food.y);
        generateFood();

        // Increase speed slightly
        if (score % 50 === 0 && gameSpeed > 50) {
            gameSpeed -= 5;
            clearInterval(gameLoop);
            gameLoop = setInterval(update, gameSpeed);
        }

        // Update high score
        if (score > highScore) {
            highScore = score;
            highScoreElement.textContent = highScore;
            localStorage.setItem('cyberSnakeHighScore', highScore);
        }
    } else {
        snake.pop();
    }
}

function update() {
    if (!isGameRunning || isPaused) return;

    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    drawGrid();
    updateParticles();
    drawFood();
    moveSnake();
    drawSnake();
}

function gameOver() {
    isGameRunning = false;
    clearInterval(gameLoop);

    finalScoreElement.textContent = score;
    gameOverScreen.style.display = 'block';
    startBtn.style.display = 'none';
    pauseBtn.style.display = 'none';
}

function startGame() {
    // Reset game state
    snake = [{ x: 10, y: 10 }];
    velocityX = 1;
    velocityY = 0;
    score = 0;
    gameSpeed = 100;
    particles = [];
    scoreElement.textContent = score;

    generateFood();

    isGameRunning = true;
    isPaused = false;
    gameOverScreen.style.display = 'none';
    startBtn.style.display = 'none';
    pauseBtn.style.display = 'inline-block';

    clearInterval(gameLoop);
    gameLoop = setInterval(update, gameSpeed);
}

function togglePause() {
    isPaused = !isPaused;
    pauseBtn.textContent = isPaused ? 'RESUME' : 'PAUSE';

    if (!isPaused) {
        gameLoop = setInterval(update, gameSpeed);
    } else {
        clearInterval(gameLoop);
    }
}

// Event listeners
startBtn.addEventListener('click', startGame);
pauseBtn.addEventListener('click', togglePause);
restartBtn.addEventListener('click', startGame);

// Keyboard controls
document.addEventListener('keydown', (e) => {
    if (!isGameRunning) return;

    switch (e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
            if (velocityY === 0) {
                velocityX = 0;
                velocityY = -1;
            }
            e.preventDefault();
            break;
        case 'ArrowDown':
        case 's':
        case 'S':
            if (velocityY === 0) {
                velocityX = 0;
                velocityY = 1;
            }
            e.preventDefault();
            break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
            if (velocityX === 0) {
                velocityX = -1;
                velocityY = 0;
            }
            e.preventDefault();
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
            if (velocityX === 0) {
                velocityX = 1;
                velocityY = 0;
            }
            e.preventDefault();
            break;
        case 'p':
        case 'P':
        case ' ':
            togglePause();
            e.preventDefault();
            break;
    }
});

// Initial draw
ctx.fillStyle = '#000000';
ctx.fillRect(0, 0, canvas.width, canvas.height);
drawGrid();
drawSnake();
drawFood();
