(function(global) {
    function ParticleNetwork(a) {
        this.canvas = a.canvas;
        this.g = a.g;
        this.particleColor = a.options.particleColor;
        this.x = Math.random() * this.canvas.width;
        this.y = Math.random() * this.canvas.height;
        this.velocity = {
            x: (Math.random() - 0.5) * a.options.velocity,
            y: (Math.random() - 0.5) * a.options.velocity
        };
    }

    ParticleNetwork.prototype.update = function() {
        if (this.x > this.canvas.width + 20 || this.x < -20) this.velocity.x = -this.velocity.x;
        if (this.y > this.canvas.height + 20 || this.y < -20) this.velocity.y = -this.velocity.y;
        this.x += this.velocity.x;
        this.y += this.velocity.y;
    };

    ParticleNetwork.prototype.draw = function() {
        this.g.beginPath();
        this.g.fillStyle = this.particleColor;
        this.g.globalAlpha = 0.7;
        this.g.arc(this.x, this.y, 1.5, 0, 2 * Math.PI);
        this.g.fill();
    };

    function ParticleCanvas(element, options) {
        this.container = element;
        this.updateContainerSize();

        options = options || {};
        this.options = {
            particleColor: options.particleColor || "#fff",
            background: options.background || "#1a252f",
            interactive: options.interactive !== undefined ? options.interactive : true,
            velocity: this.setVelocity(options.speed),
            density: this.setDensity(options.density)
        };

        this.init();
    }

    ParticleCanvas.prototype.updateContainerSize = function() {
        // ページ全体に広がるように設定
        this.container.style.width = "100%";
        this.container.style.height = "100vh";
        this.container.style.margin = "0";
        this.container.style.padding = "0";
        this.container.style.overflow = "hidden";
        
        this.container.size = {
            width: this.container.offsetWidth,
            height: this.container.offsetHeight
        };
    };

    ParticleCanvas.prototype.init = function() {
        this.container.style.position = "fixed"; // absoluteからfixedに変更
        this.container.style.top = "0";
        this.container.style.left = "0";
        this.container.style.right = "0";
        this.container.style.bottom = "0";
        this.container.style.zIndex = "-1"; // 他のコンテンツの背後に表示

        // 背景の設定
        this.backgroundDiv = document.createElement("div");
        this.backgroundDiv.style.position = "absolute";
        this.backgroundDiv.style.top = "0";
        this.backgroundDiv.style.left = "0";
        this.backgroundDiv.style.width = "100%";
        this.backgroundDiv.style.height = "100%";
        this.backgroundDiv.style.zIndex = "1";
        this.backgroundDiv.style.background = this.options.background;
        this.container.appendChild(this.backgroundDiv);

        // Canvasの作成
        this.canvas = document.createElement("canvas");
        this.canvas.width = this.container.size.width;
        this.canvas.height = this.container.size.height;
        this.canvas.style.position = "absolute";
        this.canvas.style.top = "0";
        this.canvas.style.left = "0";
        this.canvas.style.zIndex = "2";
        this.container.appendChild(this.canvas);

        this.g = this.canvas.getContext("2d");

        this.createParticles();

        if (this.options.interactive) {
            this.setupInteractivity();
        }

        // リサイズイベントの監視を改善
        window.addEventListener("resize", this.handleResize.bind(this));

        requestAnimationFrame(this.update.bind(this));
    };

    ParticleCanvas.prototype.createParticles = function() {
        this.particles = [];
        for (let i = 0; i < (this.canvas.width * this.canvas.height) / this.options.density; i++) {
            this.particles.push(new ParticleNetwork(this));
        }
    };

    ParticleCanvas.prototype.setupInteractivity = function() {
        this.mouseParticle = new ParticleNetwork(this);
        this.mouseParticle.velocity = { x: 0, y: 0 };
        this.particles.push(this.mouseParticle);

        this.canvas.addEventListener("mousemove", function(event) {
            const rect = this.canvas.getBoundingClientRect();
            this.mouseParticle.x = event.clientX - rect.left;
            this.mouseParticle.y = event.clientY - rect.top;
        }.bind(this));

        this.canvas.addEventListener("mouseup", function() {
            this.mouseParticle.velocity = {
                x: (Math.random() - 0.5) * this.options.velocity,
                y: (Math.random() - 0.5) * this.options.velocity
            };
            this.mouseParticle = new ParticleNetwork(this);
            this.mouseParticle.velocity = { x: 0, y: 0 };
            this.particles.push(this.mouseParticle);
        }.bind(this));
    };

    ParticleCanvas.prototype.handleResize = function() {
        // 即時にリサイズを適用
        this.updateContainerSize();
        this.canvas.width = this.container.size.width;
        this.canvas.height = this.container.size.height;
        
        // 粒子を再生成
        this.createParticles();
        
        // インタラクティブモードの場合はマウス粒子を追加
        if (this.options.interactive && this.mouseParticle) {
            this.particles.push(this.mouseParticle);
        }
    };

    ParticleCanvas.prototype.update = function() {
        this.g.clearRect(0, 0, this.canvas.width, this.canvas.height);

        for (let i = 0; i < this.particles.length; i++) {
            this.particles[i].update();
            this.particles[i].draw();
            for (let j = this.particles.length - 1; j > i; j--) {
                const dist = Math.sqrt(
                    Math.pow(this.particles[i].x - this.particles[j].x, 2) +
                    Math.pow(this.particles[i].y - this.particles[j].y, 2)
                );
                if (dist < 120) {
                    this.g.beginPath();
                    this.g.strokeStyle = this.options.particleColor;
                    this.g.globalAlpha = (120 - dist) / 120;
                    this.g.lineWidth = 0.7;
                    this.g.moveTo(this.particles[i].x, this.particles[i].y);
                    this.g.lineTo(this.particles[j].x, this.particles[j].y);
                    this.g.stroke();
                }
            }
        }

        if (this.options.velocity !== 0) requestAnimationFrame(this.update.bind(this));
    };

    ParticleCanvas.prototype.setVelocity = function(speed) {
        return speed === "fast" ? 1 : speed === "slow" ? 0.33 : speed === "none" ? 0 : 0.66;
    };

    ParticleCanvas.prototype.setDensity = function(density) {
        return density === "high" ? 5000 : density === "low" ? 20000 : isNaN(parseInt(density, 10)) ? 10000 : density;
    };

    // グローバルに登録
    global.ParticleNetwork = ParticleCanvas;
})(typeof window !== "undefined" ? window : this);

document.addEventListener("DOMContentLoaded", function () {
    // particle-canvasが存在しない場合は作成する
    let particleElement = document.getElementById("particle-canvas");
    if (!particleElement) {
        particleElement = document.createElement("div");
        particleElement.id = "particle-canvas";
        document.body.insertBefore(particleElement, document.body.firstChild);
    }
    
    new ParticleNetwork(particleElement, {
        particleColor: "#00ff00",
        background: "#000000",
        interactive: true,
        speed: "medium",
        density: "high"
    });
});