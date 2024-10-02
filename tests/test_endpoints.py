from datetime import date, timedelta

from fastapi import status
from httpx import AsyncClient, ASGITransport
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.db.database import get_session
from main import app
from config import API_URL


TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'


test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)

transport = ASGITransport(app=app)


async def override_get_session():
    session = TestSessionLocal()
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        yield session
    finally:
        await session.close()


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture
def test_user_data():
    return {'username': 'admin', 'password': 'Q123werty!23', 'email': 'test@test.ru'}


@pytest.fixture
def auth_headers(event_loop, test_user_data):
    async def get_headers():
        login_payload = test_user_data
        async with AsyncClient(
            transport=transport,
            base_url='http://test',
        ) as client:
            response = await client.post(
                f'{API_URL}/auth/token',
                json=login_payload,
            )
            assert response.status_code == 200, f'Login failed: {response.json()}'

            login_data = response.json()
            access_token = login_data['access_token']

            return {
                'Authorization': f'Bearer {access_token}',
            }

    return event_loop.run_until_complete(get_headers())


@pytest.fixture
def test_breed_data():
    return {
        'name': 'persian',
    }


@pytest.fixture
def multiple_test_breeds():
    return [
        {
            'name': 'siberian',
        },
        {
            'name': 'british',
        },
        {
            'name': 'scottish',
        },
    ]


@pytest.fixture
def test_kitten_data():
    return {
        'name': 'Barsik',
        'birth_date': '2023-10-12',
        'color': 'white',
        'sex': 'male',
        'description': 'bad boy',
        'breed_id': 1,
    }


@pytest.fixture
def test_edit_kitten_data():
    return {
        'name': 'Barsik',
        'birth_date': '2023-10-12',
        'color': 'black',
        'sex': 'male',
        'description': 'bad boy',
        'breed_id': 1,
    }


@pytest.fixture
def test_bad_date_kitten_data():
    future_date = date.today() + timedelta(days=10)
    past_date = date.today() - timedelta(days=365 * 25)
    return [
        {
            'name': 'Matros',
            'birth_date': f'{future_date}',
            'color': 'white',
            'sex': 'male',
            'description': 'good boy',
            'breed_id': 1,
        },
        {
            'name': 'Lara',
            'birth_date': f'{past_date}',
            'color': 'black',
            'sex': 'female',
            'description': 'bad girl',
            'breed_id': 3,
        },
    ]


@pytest.fixture
def test_non_existing_color_kitten_data():
    return {
        'name': 'barsik',
        'birth_date': '2023-10-12',
        'color': 'superblack',
        'description': 'bad boy',
        'breed_id': 2,
    }


@pytest.fixture
def test_non_existing_breed_kitten_data():
    return {
        'name': 'barsik',
        'birth_date': '2023-10-12',
        'color': 'superblack',
        'description': 'bad boy',
        'breed_id': 100,
    }


@pytest.mark.asyncio
async def test_create_user(test_user_data):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.post(f'{API_URL}/auth/user', json=test_user_data)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f'Error: {response.json()}'
        response_data = response.json()

        assert (
            test_user_data['username'] == response_data['username']
        ), f"Expected username: {test_user_data['username']}, but got: {response_data['username']}"


@pytest.mark.asyncio
async def test_create_breed(test_breed_data, auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.post(
            f'{API_URL}/breeds/', json=test_breed_data, headers=auth_headers
        )

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f'Error: {response.json()}'
        response_data = response.json()

        assert (
            test_breed_data['name'] == response_data['name']
        ), f"Expected name: {test_breed_data['name']}, but got: {response_data['name']}"


@pytest.mark.asyncio
async def test_create_same_breed(test_breed_data, auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.post(
            f'{API_URL}/breeds/', json=test_breed_data, headers=auth_headers
        )
        data = response.json()

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f'Error: {response.json()}'
        expected_error_message = 'Breed already exists'
        assert data['detail'] == expected_error_message


@pytest.mark.asyncio
async def test_create_multiple_breeds(multiple_test_breeds, auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        for breed in multiple_test_breeds:
            response = await client.post(
                f'{API_URL}/breeds/', json=breed, headers=auth_headers
            )

            assert (
                response.status_code == status.HTTP_201_CREATED
            ), f'Error: {response.json()}'
            response_data = response.json()

            assert (
                breed['name'] == response_data['name']
            ), f"Expected name: {breed['email']}, but got: {response_data['name']}"
