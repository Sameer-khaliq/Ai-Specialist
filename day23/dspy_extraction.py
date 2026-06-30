import os
import time
import dspy
import json
from dotenv import load_dotenv

load_dotenv()

lm = dspy.LM("groq/llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
dspy.configure(lm=lm)

trainset = [
    dspy.Example(
        text="We are looking for a Senior Python Developer at Stripe paying up to $180,000 base.",
        company="Stripe", role="Senior Python Developer", salary_max="180000"
    ).with_inputs("text"),
    dspy.Example(
        text="hey team, internal referral needed for a staff infra engineer at Netflix. comp is looking like 450k max base depends on exp.",
        company="Netflix", role="Staff Infra Engineer", salary_max="450000"
    ).with_inputs("text"),
    dspy.Example(
        text="OpenAI is hiring a Research Scientist for the alignment team. Must have a PhD. Competitive equity package.",
        company="OpenAI", role="Research Scientist", salary_max="None"
    ).with_inputs("text"),
    dspy.Example(
        text="[JOB_POST] || Company: Vercel || Title: Frontend Dev (Next.js) || Comp: up to $160k || Location: Remote",
        company="Vercel", role="Frontend Dev (Next.js)", salary_max="160000"
    ).with_inputs("text"),
    dspy.Example(
        text="Stealth startup in the AI space looking for a Founding Engineer. Budgeting up to 200,000 USD for the right person.",
        company="None", role="Founding Engineer", salary_max="200000"
    ).with_inputs("text"),
    dspy.Example(
        text="Contract role: Backend Node.js contributor needed at Linear. $90k - $120k max.",
        company="Linear", role="Backend Node.js contributor", salary_max="120000"
    ).with_inputs("text"),
    dspy.Example(
        text='{"pos": "Data Engineer II", "org": "Airbnb", "remuneration": {"base_limit": 195000, "currency": "USD"}}',
        company="Airbnb", role="Data Engineer II", salary_max="195000"
    ).with_inputs("text"),
    dspy.Example(
        text="While we just filled our PM role, Datadog is actively searching for a Lead QA Engineer. Max budget 175000.",
        company="Datadog", role="Lead QA Engineer", salary_max="175000"
    ).with_inputs("text"),
    dspy.Example(
        text="Spotify is expanding the Stockholm team! Seeking a Senior Product Designer. Pay is up to €110,000.",
        company="Spotify", role="Senior Product Designer", salary_max="110000"
    ).with_inputs("text"),
    dspy.Example(
        text="Join the team at Figma! We need someone awesome who knows C++ and WebAssembly inside and out. Offering 210000 max.",
        company="Figma", role="None", salary_max="210000"
    ).with_inputs("text"),
    dspy.Example(
        text="Hiring alert! Anthropic is looking for a Security Engineer. Up to $250k base + equity. DM me your resume!",
        company="Anthropic", role="Security Engineer", salary_max="250000"
    ).with_inputs("text"),
    dspy.Example(
        text="We r lookin for a SRE at Supabase. payin upto 140k.",
        company="Supabase", role="SRE", salary_max="140000"
    ).with_inputs("text")
]

devset = [
    dspy.Example(
        text="• Role: Full Stack Dev\n• Org: Retool\n• Comp cap: $165,000",
        company="Retool", role="Full Stack Dev", salary_max="165000"
    ).with_inputs("text"),
    dspy.Example(
        text="A maximum base compensation of 300000 is being allocated for the position of Principal Architect, which is currently open over at Snowflake.",
        company="Snowflake", role="Principal Architect", salary_max="300000"
    ).with_inputs("text"),
    dspy.Example(
        text="URGENT HIRING!!! DEVOPS ENGINEER NEEDED AT HUGGING FACE. SALARY UP TO 185000 USD. APPLY NOW.",
        company="Hugging Face", role="DevOps Engineer", salary_max="185000"
    ).with_inputs("text"),
    dspy.Example(
        text="Looking for someone with 5+ years of experience. Notion is hiring a Mobile Engineer (iOS) paying up to 190k base.",
        company="Notion", role="Mobile Engineer (iOS)", salary_max="190000"
    ).with_inputs("text"),
    dspy.Example(
        text="Just graduated and looking for my first tech job in web development. HMU if you have any leads!",
        company="None", role="None", salary_max="None"
    ).with_inputs("text"),
    dspy.Example(
        text="MSFT is hunting for a SWE Lead. Ceiling for this band is $225,000.",
        company="MSFT", role="SWE Lead", salary_max="225000"
    ).with_inputs("text"),
    dspy.Example(
        text="If you can tolerate moving rectangles around all day, Retool needs a UI/UX Specialist. We won't pay a penny over 130000.",
        company="Retool", role="UI/UX Specialist", salary_max="130000"
    ).with_inputs("text"),
    dspy.Example(
        text="Employment Opportunity: The firm trading as Scale AI hereby invites applications for the post of ML Platform Engineer. Compensation shall not exceed $280,000 per annum.",
        company="Scale AI", role="ML Platform Engineer", salary_max="280000"
    ).with_inputs("text"),
    dspy.Example(
        text="Contractor gig at Clerk for a Technical Writer. Paying $100/hr, maxing out at roughly 200000 a year.",
        company="Clerk", role="Technical Writer", salary_max="200000"
    ).with_inputs("text"),
    dspy.Example(
        text="Log: 2026-03-12 // RECRUIT_OPEN // Comp=Deel // Role=Solutions Engineer // Max_Band=150k //",
        company="Deel", role="Solutions Engineer", salary_max="150000"
    ).with_inputs("text"),
    dspy.Example(
        text="We don't need junior devs. Pinecone is only looking for a Senior Database Engineer. Budget caps out strictly at $240,000.",
        company="Pinecone", role="Senior Database Engineer", salary_max="240000"
    ).with_inputs("text"),
    dspy.Example(
        text="Great chatting at the conference! My team at Midjourney is actually looking for a DevRel manager right now. I think the absolute max budget approved is 170k base.",
        company="Midjourney", role="DevRel manager", salary_max="170000"
    ).with_inputs("text")
]


def baseline_groq_extractor(text: str) -> dict:
    prompt = f"""
    You are a data extraction assistant. Given a messy text paragraph containing a job description or hiring note, extract the following fields:
    - company: The name of the hiring entity. If not explicitly found, return "None".
    - role: The job title being hired for. If not explicitly found, return "None".
    - salary_max: The maximum numeric annual base salary limit mentioned. Extract ONLY digits as a string (e.g., "150000"). If k or K is used, convert to thousands. If not explicitly found or if it is unquantified, return "None".

    You must output strictly valid JSON with nothing else. No markdown wrappers, no explanations.

    Text: {text}

    JSON Output:
    """
    try:
        response = lm(prompt, max_tokens=200)
        raw_content = response[0].strip()

        if raw_content.startswith("```json"):
            raw_content = raw_content.replace("```json", "").replace("```", "").strip()
        elif raw_content.startswith("```"):
            raw_content = raw_content.replace("```", "").strip()

        return json.loads(raw_content)

    except Exception as e:
        print(f"Error during extraction: {e}")
        return {"company": "None", "role": "None", "salary_max": "None"}


class JobExtractionSignature(dspy.Signature):
    """
    Extract structured job metadata from messy, conversational, or unstructured text inputs.
    Identify the target hiring company, the specific job title, and the maximum annual base salary.
    """
    text = dspy.InputField(desc="Messy or unstructured real-world text paragraph containing job clues.")
    company = dspy.OutputField(desc="The name of the hiring company, or 'None' if missing.")
    role = dspy.OutputField(desc="The explicit job title being hired for, or 'None' if missing.")
    salary_max = dspy.OutputField(desc="The maximum annual base salary parsed as a clean digit-only string (e.g., '180000'), or 'None' if missing.")


# Predict instead of ChainOfThought - fair comparison, no extra reasoning tokens,
# avoids burning through the Groq free-tier TPM limit
dspy_program = dspy.Predict(JobExtractionSignature)


def extraction_metric(gold, pred, trace=None) -> bool:
    try:
        pred_company = getattr(pred, 'company', '') or ''
        pred_role = getattr(pred, 'role', '') or ''
        pred_salary = getattr(pred, 'salary_max', '') or ''

        gold_company = getattr(gold, 'company', '') or ''
        gold_role = getattr(gold, 'role', '') or ''
        gold_salary = getattr(gold, 'salary_max', '') or ''

        company_match = gold_company.strip().lower() == pred_company.strip().lower()
        role_match = gold_role.strip().lower() == pred_role.strip().lower()
        salary_match = gold_salary.strip().lower() == pred_salary.strip().lower()

        return bool(company_match and role_match and salary_match)

    except AttributeError:
        return False


from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(metric=extraction_metric, max_bootstrapped_demos=4)
compiled_program = optimizer.compile(dspy_program, trainset=trainset)


class PredictionPayload:
    def __init__(self, company, role, salary_max):
        self.company = company
        self.role = role
        self.salary_max = salary_max


baseline_correct = 0

print("— Evaluating Hand-Written Baseline —")
for idx, gold in enumerate(devset):
    raw_res = baseline_groq_extractor(gold.text)
    pred = PredictionPayload(
        company=raw_res.get("company", "None"),
        role=raw_res.get("role", "None"),
        salary_max=str(raw_res.get("salary_max", "None"))
    )
    score = extraction_metric(gold, pred)
    if score:
        baseline_correct += 1
    time.sleep(1.5)  # throttle to stay under Groq TPM limit

baseline_accuracy = (baseline_correct / len(devset)) * 100
print(f"Baseline Devset Accuracy: {baseline_accuracy:.2f}%")

print("\n— Evaluating DSPy Compiled Program (with throttling) —")
dspy_correct = 0
for idx, gold in enumerate(devset):
    try:
        pred = compiled_program(text=gold.text)
        score = extraction_metric(gold, pred)
        if score:
            dspy_correct += 1
        print(f"  [{idx+1}/{len(devset)}] {'PASS' if score else 'FAIL'}")
    except Exception as e:
        print(f"  [{idx+1}/{len(devset)}] ERROR: {e}")
    time.sleep(1.5)  # throttle to stay under Groq TPM limit

dspy_accuracy = (dspy_correct / len(devset)) * 100
print(f"\nDSPy Compiled Program Accuracy: {dspy_accuracy:.2f}%")

print("\n" + "=" * 50)
print("COMPARISON")
print("=" * 50)
print(f"Hand-written baseline:  {baseline_accuracy:.2f}%")
print(f"DSPy (BootstrapFewShot): {dspy_accuracy:.2f}%")
print("=" * 50)

lm.inspect_history(n=1)
