# Required Tools

Install pnpm:
[https://pnpm.io/](https://pnpm.io/)

Install uv:
[https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

# Frontend

Install the required packages for the frontend:

```bash
cd frontend
pnpm install
```

# Backend

Create a python virtual environment:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
```

Install the required packages for the backend:

```bash
pip install -r requirements.txt
```

# Running the project

In one terminal run the frontend:

```bash
cd frontend
pnpm run dev
```

And in another terminal run the backend:

```bash
cd backend
flask run
```
