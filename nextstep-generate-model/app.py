import flask
from flask import Flask, jsonify, request
from google.cloud import pubsub_v1, storage
import pickle
import tensorflow as tf
import json
import base64
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

storage_client = storage.Client()

class ResumeTemplates:
    """Class to manage resume templates"""
    _templates = {
        "Software Engineer": "Skilled in software development using languages such as Java, Python, C++, and frameworks like Spring and Hibernate. Experienced in building, testing, and maintaining software applications.",
        "Data Analyst": "Proficient in data collection, cleaning, and visualization. Skilled in using Excel, SQL, and Python to analyze datasets and provide actionable insights.",
        "Network Engineer": "Expert in configuring, managing, and troubleshooting network infrastructure, ensuring efficient data flow, and maintaining network security.",
        "Cloud Architect": "Experienced in designing and managing cloud infrastructure using platforms such as AWS, Azure, and Google Cloud. Skilled in cloud security, scalability, and cost optimization.",
        "Cybersecurity Analyst": "Skilled in protecting IT systems and networks from cyber threats. Experienced in risk analysis, penetration testing, and implementing security protocols.",
        "IT Project Manager": "Proficient in managing IT projects from initiation to completion, ensuring projects are delivered on time and within budget. Experienced in using Agile and Waterfall methodologies.",
        "Data Scientist": "Expert in using machine learning algorithms, statistical modeling, and data visualization techniques to extract insights and create predictive models from large datasets.",
        "DevOps Engineer": "Skilled in automating and optimizing processes in software development and deployment. Experienced with tools like Jenkins, Docker, Kubernetes, and cloud services.",
        "IT Support Analyst": "Provides technical support and troubleshooting for IT systems and applications. Experienced in diagnosing software and hardware issues and offering solutions to users.",
        "UX/UI Designer": "Experienced in designing user-centered interfaces and creating intuitive user experiences. Skilled in wireframing, prototyping, and using design tools like Sketch and Adobe XD.",
        "Database Analyst": "Skilled in designing, managing, and optimizing databases using SQL and other database management systems. Experienced in data migration and performance tuning.",
        "UI Developer": "Proficient in front-end web development using HTML, CSS, and JavaScript. Skilled in creating interactive, responsive user interfaces.",
        "System Administrator": "Experienced in maintaining and configuring computer systems and servers. Skilled in network administration, troubleshooting, and security implementations.",
        "AI/ML Engineer": "Proficient in developing and deploying machine learning models. Experienced in using frameworks like TensorFlow, PyTorch, and scikit-learn to create AI applications.",
        "IT Auditor": "Skilled in assessing IT systems for compliance, identifying risks, and ensuring systems are secure and adhere to industry standards.",
        "Network Security Engineer": "Experienced in securing networks and IT infrastructure. Skilled in firewall configuration, intrusion detection, and vulnerability assessments.",
        "Software Tester": "Experienced in creating and executing test plans, identifying bugs, and ensuring software products meet quality standards.",
        "Cloud Solutions Architect": "Skilled in designing and implementing scalable cloud-based solutions. Expertise in AWS, Azure, and Google Cloud platforms.",
        "IT Consultant": "Provides expert advice on IT solutions to businesses. Experienced in system design, project management, and technology integration.",
        "Front-end Developer": "Proficient in HTML, CSS, JavaScript, and front-end frameworks like React and Angular. Skilled in creating dynamic, user-friendly web pages.",
        "Business Analyst": "Skilled in analyzing business processes and data. Experienced in creating reports and recommending improvements to streamline operations.",
        "IT Helpdesk Support": "Provides first-line technical support for IT-related issues. Skilled in troubleshooting hardware, software, and network problems.",
        "DevSecOps Engineer": "Combines development, security, and operations expertise to ensure secure and efficient software delivery pipelines.",
        "Data Engineer": "Skilled in designing and building data pipelines, transforming raw data into actionable insights, and working with big data tools like Hadoop and Spark.",
        "IT Trainer": "Experienced in providing training on IT systems, software applications, and best practices. Skilled in designing learning modules and workshops.",
        "Cloud Security Engineer": "Expert in securing cloud-based infrastructure and applications. Experienced in threat modeling, encryption, and access control in cloud environments.",
        "IT Procurement Specialist": "Responsible for sourcing and purchasing IT hardware and software. Experienced in vendor management and cost optimization.",
        "UX Researcher": "Skilled in conducting user research to inform design decisions. Expertise in usability testing, user interviews, and surveys.",
        "Blockchain Developer": "Experienced in developing decentralized applications using blockchain technology. Skilled in Solidity and blockchain platforms like Ethereum.",
        "IT Risk Analyst": "Skilled in assessing and mitigating risks in IT systems. Experienced in conducting risk assessments, vulnerability analysis, and risk management strategies.",
        "Cloud Support Engineer": "Provides technical support for cloud infrastructure. Skilled in troubleshooting and optimizing cloud services to meet business needs.",
        "IT Sales Manager": "Responsible for driving sales in IT products and services. Skilled in customer relationship management, sales strategies, and product knowledge.",
        "Data Privacy Officer": "Ensures the protection of personal data and compliance with data privacy laws. Experienced in developing data protection strategies and conducting audits.",
        "Software Architect": "Experienced in designing software systems and defining architecture standards. Skilled in system integration and software design principles.",
        "IT Quality Analyst": "Skilled in ensuring software quality through testing, quality assurance procedures, and continuous improvement.",
        "Mobile App Developer": "Proficient in developing mobile applications for iOS and Android platforms. Skilled in using tools like Swift, Kotlin, and React Native.",
        "IT Procurement Manager": "Oversees procurement of IT products and services. Experienced in vendor management, contract negotiation, and budgeting.",
        "IT Compliance Officer": "Ensures that IT systems and operations comply with industry regulations and internal policies.",
        "Full-stack Developer": "Skilled in both front-end and back-end web development. Experienced in building full-stack applications using technologies like JavaScript, Node.js, and databases.",
        "IT Business Analyst": "Combines business analysis with IT expertise to bridge the gap between business needs and technology solutions.",
        "IT Trainer Assistant": "Assists in training employees on IT systems and tools. Helps in the creation of training materials and user guides.",
        "AI Ethics Consultant": "Advises on ethical considerations in AI development and deployment, ensuring fairness, transparency, and accountability in AI systems.",
        "IT Support Specialist": "Provides support for IT infrastructure, managing hardware, software, and networks to ensure seamless operations.",
        "Data Analytics Manager": "Manages data analytics teams and projects, ensuring efficient data collection, analysis, and reporting for business decision-making.",
        "IT Project Coordinator": "Coordinates IT projects from planning to execution. Manages schedules, budgets, and resources to ensure successful project delivery.",
        "Cloud Solutions Analyst": "Assists in designing cloud-based solutions and optimizations for business needs, focusing on cost-efficiency and scalability.",
        "IT Governance Manager": "Responsible for implementing IT governance policies to ensure IT systems align with business objectives and comply with regulations.",
        "Cybersecurity Engineer": "Specialized in defending IT systems from cyber-attacks. Experienced in network security, encryption, and threat prevention.",
        "IT Procurement Analyst": "Analyzes procurement processes and helps source IT products and services while optimizing costs and ensuring compliance.",
        "Data Science": """A highly skilled professional with expertise in Python, machine learning, and data analysis. Experienced in creating predictive models and generating actionable insights.""",
        "HR": """A human resources professional with extensive experience in recruitment, employee relations, and performance management. Skilled in fostering a positive workplace culture.""",
        "Advocate": """A qualified advocate with in-depth knowledge of legal systems, drafting contracts, and representing clients in court. Adept at providing strategic legal advice.""",
        "Arts": """A creative individual skilled in various art forms including painting, sculpture, and digital design. Passionate about expressing ideas through visual storytelling.""",
        "Web Designing": """Expert in web development using HTML5, CSS3, and JavaScript. Skilled in front-end frameworks like Bootstrap and building responsive websites.""",
        "Mechanical Engineer": """An experienced mechanical engineer specializing in CAD/CAM, thermal engineering, and robotics. Adept at solving complex engineering problems.""",
        "Sales": """A results-driven sales professional skilled in building client relationships, closing deals, and meeting sales targets. Experienced in B2B and B2C environments.""",
        "Health and Fitness": """A certified fitness trainer with expertise in creating personalized workout plans, nutrition guidance, and promoting overall wellness.""",
        "Civil Engineer": """A proficient civil engineer skilled in project management, structural design, and site supervision. Adept at using tools like AutoCAD and SAP2000.""",
        "Java Developer": """Proficient in Java, J2EE, Spring, and Hibernate. Experienced in building scalable enterprise applications and backend systems.""",
        "Business Analyst": """An analytical professional with expertise in gathering requirements, process improvement, and stakeholder management. Skilled in tools like Tableau and Excel.""",
        "SAP Developer": """An experienced SAP developer skilled in ABAP, Fiori, and SAP HANA. Adept at implementing and optimizing SAP solutions for business needs.""",
        "Automation Testing": """An automation testing expert proficient in Selenium, Appium, and JMeter. Experienced in creating robust automated test scripts.""",
        "Electrical Engineering": """A skilled electrical engineer with expertise in circuit design, power systems, and renewable energy solutions. Proficient in tools like MATLAB and PSCAD.""",
        "Operations Manager": """An operations manager with extensive experience in supply chain management, resource allocation, and improving operational efficiency.""",
        "Python Developer": """A Python developer skilled in building web applications, data analysis, and scripting. Experienced with frameworks like Django and Flask.""",
        "DevOps Engineer": """A DevOps engineer with expertise in CI/CD pipelines, containerization using Docker, and orchestration with Kubernetes. Skilled in cloud platforms like AWS and Azure.""",
        "Network Security Engineer": """A network security engineer specializing in securing IT infrastructures, implementing firewalls, and conducting vulnerability assessments.""",
        "PMO": """A project management professional skilled in project planning, resource management, and ensuring timely delivery of milestones.""",
        "Database": """A database expert with hands-on experience in database design, optimization, and administration. Skilled in MySQL, PostgreSQL, and MongoDB.""",
        "Hadoop": """A big data specialist with expertise in Hadoop ecosystem, including HDFS, MapReduce, Hive, and Spark. Skilled in data ingestion and processing.""",
        "ETL Developer": """An ETL developer experienced in designing and implementing ETL pipelines using tools like Informatica and Talend. Skilled in data integration and transformation.""",
        "DotNet Developer": """A .NET developer with expertise in building web and desktop applications using C#, ASP.NET, and MVC frameworks.""",
        "Blockchain": """A blockchain developer with knowledge of smart contracts, Ethereum, and decentralized application (dApp) development. Skilled in Solidity and Hyperledger.""",
        "Testing": """A quality assurance professional skilled in manual and automated testing. Proficient in tools like Selenium, Postman, and JIRA."""
    }

    @classmethod
    def get_template(cls, category: str) -> str:
        return cls._templates.get(category, "Sorry, no description available for this category.")

class MLGenerateService:
    def __init__(self):
        try:
            self.publisher = pubsub_v1.PublisherClient()
            self.project_id = 'next-step-442801'
            self.topic_name = 'ml-generate-result'
            self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
        except Exception as e:
            logger.error(f"Failed to initialize MLGenerateService: {e}")
            raise

    def publish_prediction_result(self, data: dict) -> None:
        try:
            message_data = json.dumps(data).encode('utf-8')
            future = self.publisher.publish(self.topic_path, data=message_data)
            message_id = future.result()
            logger.info(f"Published message {message_id} to {self.topic_path}")
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            raise

class ModelLoader:
    @staticmethod
    def download_from_gcs(bucket_name: str, source_blob_name: str, destination_file_name: str):
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        logger.info(f"Downloaded {source_blob_name} to {destination_file_name}")

    @staticmethod
    def load_models(bucket_name='nextstep-model-generate'):
        try:
            ModelLoader.download_from_gcs(bucket_name, 'best_resume_classifier_model.h5', 'model.h5')
            ModelLoader.download_from_gcs(bucket_name, 'label_encoder.pickle', 'label_encoder.pickle')
            ModelLoader.download_from_gcs(bucket_name, 'tokenizer.pickle', 'tokenizer.pickle')

            model = tf.keras.models.load_model('model.h5')
            with open('tokenizer.pickle', 'rb') as handle:
                tokenizer = pickle.load(handle)
            with open('label_encoder.pickle', 'rb') as handle:
                label_encoder = pickle.load(handle)
            return model, tokenizer, label_encoder
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise

def create_app() -> Flask:
    """Create and configure Flask application"""
    app = Flask(__name__)
    generate_service = MLGenerateService()
    
    # Load models at startup
    try:
        model, tokenizer, label_encoder = ModelLoader.load_models()
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

    @app.route('/', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({'status': 'ML Service is running', 'version': '1.0'}), 200

    @app.route('/generate', methods=['POST'])
    def generate():
        """Generate resume description based on career"""
        try:
            # Validate request
            envelope = request.get_json()
            if not envelope or "message" not in envelope:
                logger.error("Invalid Pub/Sub message format")
                return jsonify({'error': 'Invalid Pub/Sub message format'}), 400

            # Decode message
            pubsub_message = envelope["message"]
            if "data" not in pubsub_message:
                logger.error("No data field in Pub/Sub message")
                return jsonify({'error': 'No data field in Pub/Sub message'}), 400

            message_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
            decoded_message = json.loads(message_data)

            # Validate required fields
            request_id = decoded_message.get("request_id")
            career = decoded_message.get("career")
            if not request_id or not career:
                logger.error("Missing required fields in request")
                return jsonify({'error': 'Missing required fields'}), 400

            # Generate resume description
            resume_description = ResumeTemplates.get_template(career)
            
            # Prepare response
            generated_resume_data = {
                'request_id': request_id,
                'career': career,
                'resume': resume_description,
            }

            # Publish result
            generate_service.publish_prediction_result(generated_resume_data)

            return jsonify(generated_resume_data), 200
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return jsonify({'error': 'Invalid JSON format'}), 200
        except Exception as e:
            logger.error(f"Unexpected error in generate endpoint: {e}")
            return jsonify({'error': 'Internal server error'}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)