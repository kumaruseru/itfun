// A React component to render the Three.js scene as a background
const ThreeScene = () => {
    // useRef hook to get a reference to the canvas element
    const mountRef = React.useRef(null);

    // useEffect hook to set up the Three.js scene once the component mounts
    React.useEffect(() => {
        const currentMount = mountRef.current;
        
        // Scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: currentMount, antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        camera.position.z = 10;

        // Create a central star with a corona effect
        const starGeometry = new THREE.SphereGeometry(1.5, 64, 64);
        const starMaterial = new THREE.MeshBasicMaterial({ color: 0xADD8E6, transparent: true, opacity: 0.9 });
        const star = new THREE.Mesh(starGeometry, starMaterial);

        const coronaGeometry = new THREE.SphereGeometry(1.7, 64, 64);
        const coronaMaterial = new THREE.MeshBasicMaterial({ color: 0x00BFFF, transparent: true, opacity: 0.3, blending: THREE.AdditiveBlending });
        const corona = new THREE.Mesh(coronaGeometry, coronaMaterial);

        const starGroup = new THREE.Group();
        starGroup.add(star);
        starGroup.add(corona);
        scene.add(starGroup);
        
        // Create a starfield background
        const starfieldGeometry = new THREE.BufferGeometry();
        const starfieldCount = 8000;
        const starfieldPos = new Float32Array(starfieldCount * 3);
        for(let i = 0; i < starfieldCount * 3; i++) { 
            starfieldPos[i] = (Math.random() - 0.5) * 100; 
        }
        starfieldGeometry.setAttribute('position', new THREE.BufferAttribute(starfieldPos, 3));
        
        // Function to create a texture for the star particles
        function createStarTexture() {
            const canvas = document.createElement('canvas');
            canvas.width = 64;
            canvas.height = 64;
            const context = canvas.getContext('2d');
            const gradient = context.createRadialGradient(32, 32, 0, 32, 32, 32);
            gradient.addColorStop(0, 'rgba(255,255,255,1)');
            gradient.addColorStop(0.2, 'rgba(255,255,255,0.8)');
            gradient.addColorStop(1, 'rgba(255,255,255,0)');
            context.fillStyle = gradient;
            context.fillRect(0, 0, 64, 64);
            return new THREE.CanvasTexture(canvas);
        }

        const starfieldMaterial = new THREE.PointsMaterial({
            size: 0.25,
            map: createStarTexture(),
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
        });
        const starfield = new THREE.Points(starfieldGeometry, starfieldMaterial);
        scene.add(starfield);

        // Create a nebula effect with colored particles
        const nebulaGeometry = new THREE.BufferGeometry();
        const nebulaCount = 200;
        const nebulaPos = new Float32Array(nebulaCount * 3);
        const nebulaColors = new Float32Array(nebulaCount * 3);
        const nebulaColor = new THREE.Color();
        for(let i = 0; i < nebulaCount; i++) {
            const i3 = i * 3;
            nebulaPos[i3] = (Math.random() - 0.5) * 50;
            nebulaPos[i3 + 1] = (Math.random() - 0.5) * 30;
            nebulaPos[i3 + 2] = (Math.random() - 0.5) * 30 - 20;
            nebulaColor.set(Math.random() > 0.5 ? 0x8A2BE2 : 0x00BFFF);
            nebulaColor.toArray(nebulaColors, i3);
        }
        nebulaGeometry.setAttribute('position', new THREE.BufferAttribute(nebulaPos, 3));
        nebulaGeometry.setAttribute('color', new THREE.BufferAttribute(nebulaColors, 3));
        
        // Function to create a texture for the nebula particles
        function createNebulaTexture() {
            const canvas = document.createElement('canvas');
            canvas.width = 128;
            canvas.height = 128;
            const context = canvas.getContext('2d');
            const gradient = context.createRadialGradient(64, 64, 0, 64, 64, 64);
            gradient.addColorStop(0, 'rgba(255,255,255,1)');
            gradient.addColorStop(0.2, 'rgba(255,255,255,0.7)');
            gradient.addColorStop(0.5, 'rgba(255,255,255,0.2)');
            gradient.addColorStop(1, 'rgba(255,255,255,0)');
            context.fillStyle = gradient;
            context.fillRect(0, 0, 128, 128);
            return new THREE.CanvasTexture(canvas);
        }

        const nebulaMaterial = new THREE.PointsMaterial({
            size: 15,
            map: createNebulaTexture(),
            transparent: true,
            blending: THREE.AdditiveBlending,
            opacity: 0.2,
            vertexColors: true,
            depthWrite: false,
        });
        const nebula = new THREE.Points(nebulaGeometry, nebulaMaterial);
        scene.add(nebula);

        // Mouse move listener to create a parallax effect
        let mouseX = 0, mouseY = 0;
        const onDocumentMouseMove = (event) => {
            mouseX = (event.clientX - window.innerWidth / 2) / 100;
            mouseY = (event.clientY - window.innerHeight / 2) / 100;
        };
        document.addEventListener('mousemove', onDocumentMouseMove);

        // Animation loop
        const clock = new THREE.Clock();
        const animate = () => {
            requestAnimationFrame(animate);
            const elapsedTime = clock.getElapsedTime();
            
            // Rotate objects
            starGroup.rotation.y = elapsedTime * 0.1;
            starGroup.rotation.x = elapsedTime * 0.05;
            nebula.rotation.y = elapsedTime * 0.02;

            // Move camera based on mouse position for parallax effect
            camera.position.x += (mouseX - camera.position.x) * 0.02;
            camera.position.y += (-mouseY - camera.position.y) * 0.02;
            camera.lookAt(scene.position);
            
            renderer.render(scene, camera);
        };
        animate();

        // Handle window resize
        const handleResize = () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        };
        window.addEventListener('resize', handleResize);

        // Cleanup function to remove event listeners when the component unmounts
        return () => {
            window.removeEventListener('resize', handleResize);
            document.removeEventListener('mousemove', onDocumentMouseMove);
        };
    }, []);

    return <canvas ref={mountRef} id="bg-canvas" />;
};

// SVG icon for COWN
const COWNIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#00BFFF" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2a10 10 0 1 0 10 10" /><path d="M12 12a5 5 0 1 0-5-5" /><path d="M12 12a2 2 0 1 0-2-2" /><path d="M12 22a10 10 0 0 0 10-10" />
    </svg>
);

// A custom select dropdown component
const CustomSelect = ({ options, placeholder, value, onChange }) => {
    const [isOpen, setIsOpen] = React.useState(false);
    const selectRef = React.useRef(null);

    const handleOptionClick = (optionValue) => {
        onChange(optionValue);
        setIsOpen(false);
    };

    React.useEffect(() => {
        const handleClickOutside = (event) => {
            if (selectRef.current && !selectRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [selectRef]);

    const displayValue = options.find(opt => opt.value === value)?.label || placeholder;

    return (
        <div className="relative w-full" ref={selectRef}>
            <button type="button" onClick={() => setIsOpen(!isOpen)} className="w-full p-3 text-left rounded-lg custom-select-trigger">
                <span className={value ? 'text-white' : 'text-gray-400'}>{displayValue}</span>
            </button>
            {isOpen && (
                <div className="custom-select-panel">
                    {options.map((option) => (
                        <div key={option.value} onClick={() => handleOptionClick(option.value)} className="custom-select-option">
                            {option.label}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

// The main App component that renders the registration form
const App = () => {
    const [formData, setFormData] = React.useState({ day: '', month: '', year: '', gender: '' });

    const handleSelectChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const currentYear = new Date().getFullYear();
    const yearOptions = Array.from({ length: 100 }, (_, i) => ({ value: currentYear - i, label: currentYear - i }));
    const monthOptions = Array.from({ length: 12 }, (_, i) => ({ value: i + 1, label: `Tháng ${i + 1}` }));
    const dayOptions = Array.from({ length: 31 }, (_, i) => ({ value: i + 1, label: i + 1 }));
    const genderOptions = [ { value: 'male', label: 'Nam' }, { value: 'female', label: 'Nữ' }, { value: 'other', label: 'Khác' }];

    return (
        <>
            <ThreeScene />
            <div className="w-full max-w-md p-6 sm:p-8 space-y-6 rounded-2xl shadow-2xl form-container">
                <div className="text-center space-y-2">
                    <div className="flex justify-center"><COWNIcon /></div>
                    <h1 className="text-3xl font-bold text-white">Tham gia COWN</h1>
                    <p className="text-gray-300">Tạo tài khoản để kết nối với bạn bè</p>
                </div>
                <div className="w-full space-y-4">
                    <div className="flex flex-col sm:flex-row gap-4">
                        <input type="text" placeholder="Họ" className="w-full p-3 rounded-lg form-input" />
                        <input type="text" placeholder="Tên" className="w-full p-3 rounded-lg form-input" />
                    </div>
                    <div>
                        <label className="text-sm text-gray-400 mb-1 block">Ngày sinh</label>
                        <div className="flex gap-2 sm:gap-4">
                            <CustomSelect options={dayOptions} placeholder="Ngày" value={formData.day} onChange={(val) => handleSelectChange('day', val)} />
                            <CustomSelect options={monthOptions} placeholder="Tháng" value={formData.month} onChange={(val) => handleSelectChange('month', val)} />
                            <CustomSelect options={yearOptions} placeholder="Năm" value={formData.year} onChange={(val) => handleSelectChange('year', val)} />
                        </div>
                    </div>
                    <div>
                        <label className="text-sm text-gray-400 mb-1 block">Giới tính</label>
                         <CustomSelect options={genderOptions} placeholder="Chọn giới tính" value={formData.gender} onChange={(val) => handleSelectChange('gender', val)} />
                    </div>
                    <input type="email" placeholder="Nhập email của bạn" className="w-full p-3 rounded-lg form-input" />
                    <input type="password" placeholder="Tạo mật khẩu mới" className="w-full p-3 rounded-lg form-input" />
                    <input type="password" placeholder="Nhập lại mật khẩu" className="w-full p-3 rounded-lg form-input" />
                    <button className="w-full p-3 rounded-lg font-bold form-button !mt-6">Tạo Tài Khoản</button>
                    <p className="text-center text-gray-300 text-sm !mt-4">Đã có tài khoản? <a href="login.html" className="font-semibold form-link transition">Đăng nhập ngay</a></p>
                </div>
            </div>
        </>
    );
};

// Render the main App component into the 'root' div
ReactDOM.render(<App />, document.getElementById('root'));
