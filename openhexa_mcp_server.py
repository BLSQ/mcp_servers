"""
MCP OpenHEXA Server - Main server implementation using FastMCP
"""

import base64
import io
import json
import os
import sys
import zipfile
from typing import Any

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP


# Load environment variables if available
load_dotenv()

# Import OpenHEXA SDK after loading environment variables.
try:
    from openhexa.sdk.client import openhexa
except Exception:
    openhexa = None

# Check SDK availability and required credentials.
OPENHEXA_AVAILABLE = bool(openhexa) and bool(os.environ.get("HEXA_SERVER_URL")) and bool(
    os.environ.get("HEXA_TOKEN")
)


# Create the MCP server
mcp = FastMCP("OpenHEXA")


@mcp.tool
def list_workspaces(page: int = 1, per_page: int = 10) -> dict:
    """
    List all available workspaces.

    Args:
        page: Page number (default: 1)
        per_page: Number of workspaces per page (default: 10)

    Returns:
        Dict containing workspaces and pagination information:
        - workspaces: List of workspace objects
        - total_pages: Total number of pages available
        - current_page: Current page number
        - per_page: Number of items per page
        - count: Number of items in current page
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        workspaces_page = openhexa.workspaces(page=page, per_page=per_page)
        return {
            "workspaces": [w.model_dump() for w in workspaces_page.items],
            "total_pages": workspaces_page.total_pages,
            "current_page": page,
            "per_page": per_page,
            "count": len(workspaces_page.items),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def get_workspace_details(workspace_slug: str) -> dict:
    """Get details for a specific workspace."""
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        workspace = openhexa.workspace(slug=workspace_slug)
        if workspace:
            return workspace.model_dump()
        else:
            return {"error": f"Workspace '{workspace_slug}' not found"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def list_datasets(
    page: int = 1, per_page: int = 10, workspace_slug: str | None = None
) -> dict:
    """
    List datasets.

    Args:
        page: Page number (default: 1)
        per_page: Number of datasets per page (default: 10)
        workspace_slug: Optional workspace slug to scope datasets

    Returns:
        Dict containing datasets and pagination information:
        - datasets: List of dataset objects
        - total_pages: Total number of pages available
        - current_page: Current page number
        - per_page: Number of items per page
        - count: Number of items in current page
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        datasets_page = openhexa.datasets(page=page, per_page=per_page)
        datasets = [d.model_dump() for d in datasets_page.items]
        if workspace_slug:
            datasets = [
                d
                for d in datasets
                if d.get("workspace", {}).get("slug") == workspace_slug
            ]
        return {
            "datasets": datasets,
            "total_pages": datasets_page.total_pages,
            "current_page": page,
            "per_page": per_page,
            "count": len(datasets),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def get_dataset_details(dataset_id: str) -> dict:
    """Get details for a specific dataset by ID."""
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        dataset = openhexa.dataset(id=dataset_id)
        if dataset:
            return dataset.model_dump()
        else:
            return {"error": f"Dataset with ID '{dataset_id}' not found"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def list_pipelines(workspace_slug: str, page: int = 1, per_page: int = 10) -> dict:
    """
    List pipelines for a workspace.

    Args:
        workspace_slug: The workspace slug
        page: Page number (default: 1)
        per_page: Number of pipelines per page (default: 10)

    Returns:
        Dict containing pipelines and pagination information:
        - pipelines: List of pipeline objects
        - total_pages: Total number of pages available
        - current_page: Current page number
        - per_page: Number of items per page
        - count: Number of items in current page
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        pipelines_page = openhexa.pipelines(
            workspace_slug=workspace_slug, page=page, per_page=per_page
        )
        return {
            "pipelines": [p.model_dump() for p in pipelines_page.items],
            "total_pages": pipelines_page.total_pages,
            "current_page": page,
            "per_page": per_page,
            "count": len(pipelines_page.items),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def get_pipeline_details(workspace_slug: str, pipeline_code: str) -> dict:
    """Get details for a specific pipeline in a workspace."""
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        pipeline = openhexa.pipeline(workspace_slug=workspace_slug, pipeline_code=pipeline_code)
        if pipeline:
            return pipeline.model_dump()
        else:
            return {
                "error": f"Pipeline '{pipeline_code}' not found in workspace '{workspace_slug}'"
            }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def get_pipeline_runs(workspace_slug: str, pipeline_code: str) -> dict:
    """Get runs for a specific pipeline in a workspace."""
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        pipeline = openhexa.pipeline(workspace_slug=workspace_slug, pipeline_code=pipeline_code)
        if pipeline:
            runs = pipeline.runs
            return {"runs": [r.model_dump() for r in runs.items], "count": len(runs.items)}
        else:
            return {
                "error": f"Pipeline '{pipeline_code}' not found in workspace '{workspace_slug}'"
            }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def list_workspace_members(workspace_slug: str) -> dict:
    """List members of a workspace."""
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        members = openhexa.get_users(query="", workspace_slug=workspace_slug)
        return {"members": [m.model_dump() for m in members], "count": len(members)}
    except Exception as e:
        return {"error": str(e)}


def _create_pipeline_zipfile(code_content: str) -> str:
    """
    Create a base64-encoded ZIP file containing pipeline code.

    The ZIP should have this structure:
    pipeline.zip
    └── pipeline.py  (contains the code_content)

    Args:
        code_content: Python code as string

    Returns:
        Base64-encoded ZIP file string
    """
    # Create in-memory ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("pipeline.py", code_content)

    # Get ZIP bytes and encode to base64
    zip_bytes = zip_buffer.getvalue()
    return base64.b64encode(zip_bytes).decode("utf-8")


@mcp.tool
def create_pipeline(
    workspace_slug: str,
    name: str,
    code_content: str,
    description: str | None = None,
    functional_type: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Create a new pipeline with code in a workspace.

    Args:
        workspace_slug: The workspace slug where to create the pipeline
        name: Pipeline name (code will be auto-generated from this)
        code_content: Python code for the pipeline (will be packaged as ZIP)
        description: Optional pipeline description
        functional_type: Optional type: extraction, transformation, loading, or computation
        tags: Optional list of tags

    Returns:
        Dict containing the created pipeline details and upload status
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        # Validate inputs
        if not workspace_slug or not name or not code_content:
            return {"error": "workspace_slug, name, and code_content are required"}

        # Step 1: Create the pipeline entity
        create_query = """
            mutation createPipeline($input: CreatePipelineInput!) {
                createPipeline(input: $input) {
                    success
                    errors
                    pipeline {
                        id
                        name
                        code
                        type
                        workspace { slug }
                    }
                }
            }
        """

        create_input = {
            "name": name,
            "workspaceSlug": workspace_slug,
        }

        if functional_type:
            create_input["functionalType"] = functional_type.lower()

        if tags:
            create_input["tags"] = tags

        create_variables = {"input": create_input}

        result = openhexa.execute(query=create_query, variables=create_variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        create_result = response_data.get("data", {}).get("createPipeline", {})

        if not create_result.get("success"):
            errors = create_result.get("errors", [])
            return {"error": f"Failed to create pipeline: {errors}"}

        pipeline = create_result.get("pipeline")
        if not pipeline:
            return {"error": "Pipeline creation succeeded but no pipeline data returned"}

        pipeline_code = pipeline["code"]

        # Step 2: Package code into ZIP
        try:
            zipfile_b64 = _create_pipeline_zipfile(code_content)
        except Exception as e:
            return {
                "error": f"Failed to create ZIP file: {str(e)}",
                "pipeline": pipeline,
                "note": "Pipeline was created but code upload failed",
            }

        # Step 3: Upload the code
        upload_query = """
            mutation uploadPipeline($input: UploadPipelineInput!) {
                uploadPipeline(input: $input) {
                    success
                    errors
                }
            }
        """

        upload_input = {
            "workspaceSlug": workspace_slug,
            "pipelineCode": pipeline_code,
            "name": "Initial version",
            "description": description or "Created via MCP",
            "zipfile": zipfile_b64,
        }

        upload_variables = {"input": upload_input}

        upload_result = openhexa.execute(query=upload_query, variables=upload_variables)
        upload_response_data = upload_result.json()

        if "errors" in upload_response_data:
            return {
                "error": f"GraphQL error during upload: {upload_response_data['errors']}",
                "pipeline": pipeline,
                "note": "Pipeline was created but code upload failed",
            }

        upload_result_data = upload_response_data.get("data", {}).get("uploadPipeline", {})

        if not upload_result_data.get("success"):
            errors = upload_result_data.get("errors", [])
            return {
                "error": f"Failed to upload pipeline code: {errors}",
                "pipeline": pipeline,
                "note": "Pipeline was created but code upload failed",
            }

        return {
            "success": True,
            "pipeline": pipeline,
            "message": f"Pipeline '{name}' created and code uploaded successfully",
        }

    except Exception as e:
        return {"error": f"Failed to create pipeline: {str(e)}"}


@mcp.tool
def list_connections(workspace_slug: str) -> dict[str, Any]:
    """
    List connections in a specific workspace.

    Args:
        workspace_slug: The workspace slug

    Returns:
        Dict containing connection information
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        query = """
        query WorkspaceConnections($slug: String!) {
            workspace(slug: $slug) {
                connections {
                    id
                    name
                    slug
                    description
                    type
                    createdAt
                    updatedAt
                    user {
                        id
                        displayName
                        email
                    }
                    fields {
                        code
                        value
                        secret
                    }
                }
            }
        }
        """

        variables = {"slug": workspace_slug}

        result = openhexa.execute(query, variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        workspace = response_data.get("data", {}).get("workspace")
        if not workspace:
            return {"error": f"Workspace '{workspace_slug}' not found"}

        connections = workspace.get("connections", [])

        return {"connections": connections, "count": len(connections)}

    except Exception as e:
        return {"error": f"Failed to list connections: {str(e)}"}


@mcp.tool
def list_webapps(workspace_slug: str, page: int = 1, per_page: int = 10) -> dict[str, Any]:
    """
    List webapps in a specific workspace.

    Args:
        workspace_slug: The workspace slug
        page: Page number (default: 1)
        per_page: Number of webapps per page (default: 10)

    Returns:
        Dict containing webapp information
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        query = """
        query WorkspaceWebapps($slug: String!, $page: Int = 1, $perPage: Int = 10) {
            workspace(slug: $slug) {
                webapps(page: $page, perPage: $perPage) {
                    items {
                        id
                        name
                        description
                        url
                        icon
                        isFavorite
                        createdAt
                        createdBy {
                            id
                            displayName
                            email
                        }
                        permissions {
                            delete
                            update
                        }
                    }
                    pageNumber
                    totalItems
                    totalPages
                }
            }
        }
        """

        variables = {"slug": workspace_slug, "page": page, "perPage": per_page}

        result = openhexa.execute(query, variables)
        response_data = result.json()

        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}

        workspace = response_data.get("data", {}).get("workspace")
        if not workspace:
            return {"error": f"Workspace '{workspace_slug}' not found"}

        webapps_data = workspace.get("webapps", {})

        return {
            "webapps": webapps_data.get("items", []),
            "total_pages": webapps_data.get("totalPages", 0),
            "total_items": webapps_data.get("totalItems", 0),
            "current_page": webapps_data.get("pageNumber", page),
        }

    except Exception as e:
        return {"error": f"Failed to list webapps: {str(e)}"}


@mcp.tool
def search_resources(
    query: str, resource_type: str | None = None, workspace_slug: str | None = None
) -> dict[str, Any]:
    """
    Search across OpenHEXA resources (workspaces, datasets, pipelines).

    Args:
        query: Search query string
        resource_type: Optional filter by resource type ('workspace', 'dataset', 'pipeline')
        workspace_slug: Optional workspace slug to limit search scope

    Returns:
        Dict containing search results
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}

    try:
        results = {"success": True, "query": query, "results": []}

        # Search workspaces
        if not resource_type or resource_type == "workspace":
            workspace_results = list_workspaces()
            if workspace_results.get("success"):
                for workspace in workspace_results.get("workspaces", []):
                    if (
                        query.lower() in workspace.get("name", "").lower()
                        or query.lower() in workspace.get("description", "").lower()
                    ):
                        results["results"].append({"type": "workspace", "resource": workspace})

        # Search datasets
        if not resource_type or resource_type == "dataset":
            dataset_results = list_datasets(workspace_slug=workspace_slug)
            if dataset_results.get("success"):
                for dataset in dataset_results.get("datasets", []):
                    dataset_obj = dataset.get("dataset", dataset)  # Handle nested structure
                    if (
                        query.lower() in dataset_obj.get("name", "").lower()
                        or query.lower() in dataset_obj.get("description", "").lower()
                    ):
                        results["results"].append({"type": "dataset", "resource": dataset_obj})

        # Search pipelines
        if not resource_type or resource_type == "pipeline":
            pipeline_results = list_pipelines(workspace_slug=workspace_slug)
            if pipeline_results.get("success"):
                for pipeline in pipeline_results.get("pipelines", []):
                    if (
                        query.lower() in pipeline.get("name", "").lower()
                        or query.lower() in pipeline.get("description", "").lower()
                    ):
                        results["results"].append({"type": "pipeline", "resource": pipeline})

        results["count"] = len(results["results"])
        return results

    except Exception as e:
        return {"error": f"Failed to search resources: {str(e)}"}


@mcp.tool
def list_dataset_versions(dataset_id: str) -> dict[str, Any]:
    """
    List all versions of a dataset.
    Args:
        dataset_id: The ID identifier for the dataset
    Returns:
        Dict containing dataset version information
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query getDataset($id: ID!) {
            dataset(id: $id) {
                versions {
                    items {
                        id
                        name
                        changelog
                        createdAt
                        createdBy {
                            id
                            displayName
                            email
                        }
                    }
                }
            }
        }
        """
        result = openhexa.execute(query=query, variables={"id": dataset_id})
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}
        dataset = response_data.get("data", {}).get("dataset")
        if not dataset:
            return {"error": f"Dataset '{dataset_id}' not found"}
        versions = dataset.get("versions", {}).get("items", [])
        return {"versions": versions, "count": len(versions)}
    except Exception as e:
        return {"error": f"Failed to list dataset versions: {str(e)}"}


@mcp.tool
def get_dataset_version_details(version_id: str) -> dict[str, Any]:
    """
    Get detailed information about a specific dataset version.
    Args:
        version_id: The ID of the dataset version
    Returns:
        Dict containing detailed dataset version information
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query getDatasetVersion($id: ID!) {
            datasetVersion(id: $id) {
                id
                name
                changelog
                createdAt
                createdBy {
                    id
                    displayName
                    email
                }
                files {
                    items {
                        id
                        size
                        createdAt
                    }
                }
            }
        }
        """
        result = openhexa.execute(query=query, variables={"id": version_id})
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}
        version = response_data.get("data", {}).get("datasetVersion")
        if not version:
            return {"error": f"Dataset version '{version_id}' not found"}
        return {"version": version}
    except Exception as e:
        return {"error": f"Failed to get dataset version details: {str(e)}"}


@mcp.tool
def list_dataset_files(dataset_id: str) -> dict[str, Any]:
    """
    List all files for all versions of a dataset.
    Args:
        dataset_id: The ID identifier for the dataset
    Returns:
        Dict containing all files for all versions
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query getDataset($id: ID!) {
            dataset(id: $id) {
                versions {
                    items {
                        id
                        name
                        files {
                            items {
                                id
                                size
                                createdAt
                            }
                        }
                    }
                }
            }
        }
        """
        result = openhexa.execute(query=query, variables={"id": dataset_id})
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}", "raw": response_data}
        dataset = response_data.get("data", {}).get("dataset")
        if not dataset:
            return {"error": f"Dataset '{dataset_id}' not found"}
        files = []
        for version in dataset.get("versions", {}).get("items", []):
            for file in version.get("files", {}).get("items", []):
                files.append({**file, "version_id": version["id"], "version_name": version["name"]})
        return {"files": files, "count": len(files)}
    except Exception as e:
        return {"error": f"Failed to list dataset files: {str(e)}"}


@mcp.tool
def get_dataset_file_details(file_id: str) -> dict[str, Any]:
    """
    Get details for a specific dataset file.
    Args:
        file_id: The ID of the file
    Returns:
        Dict containing file metadata
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query getFile($id: ID!) {
            datasetVersionFile(id: $id) {
                id
                filename
                size
                contentType
                createdAt
                createdBy {
                    id
                    displayName
                    email
                }
                downloadUrl
                uri
            }
        }
        """
        variables = {"id": file_id}
        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}
        file = response_data.get("data", {}).get("datasetVersionFile")
        if not file:
            return {"error": f"File '{file_id}' not found"}
        return {"file": file}
    except Exception as e:
        return {"error": f"Failed to get file details: {str(e)}"}


@mcp.tool
def search_datasets(query_str: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
    """
    Search datasets by name or description.

    Args:
        query_str: Search string
        page: Page number (default: 1)
        per_page: Number of results per page (default: 20)

    Returns:
        Dict containing datasets and pagination information:
        - datasets: List of dataset objects
        - total_pages: Total number of pages available
        - current_page: Current page number
        - per_page: Number of items per page
        - count: Number of items in current page
        - total_items: Total number of items across all pages
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query searchDatasets($query: String, $page: Int!, $perPage: Int!) {
            datasets(query: $query, page: $page, perPage: $perPage) {
                items {
                    id
                    name
                    slug
                    description
                    createdAt
                    updatedAt
                    createdBy {
                        id
                        displayName
                        email
                    }
                }
                totalItems
                totalPages
            }
        }
        """
        variables = {"query": query_str, "page": page, "perPage": per_page}
        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}
        datasets_info = response_data.get("data", {}).get("datasets", {})
        datasets = datasets_info.get("items", [])
        total_items = datasets_info.get("totalItems", 0)
        total_pages = datasets_info.get("totalPages", 0)
        return {
            "datasets": datasets,
            "count": len(datasets),
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page,
        }
    except Exception as e:
        return {"error": f"Failed to search datasets: {str(e)}"}


@mcp.tool
def list_datasets_by_creator(
    creator_email: str, page: int = 1, per_page: int = 20
) -> dict[str, Any]:
    """
    List datasets created by a specific user.
    Args:
        creator_email: The email of the creator
        page: Page number (default: 1)
        per_page: Number of results per page (default: 20)
    Returns:
        Dict containing datasets by creator
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query datasetsByCreator($page: Int!, $perPage: Int!) {
            datasets(page: $page, perPage: $perPage) {
                items {
                    id
                    name
                    slug
                    description
                    createdAt
                    updatedAt
                    createdBy {
                        id
                        displayName
                        email
                    }
                }
                totalItems
                totalPages
            }
        }
        """
        variables = {"page": page, "perPage": per_page}
        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}"}
        datasets = response_data.get("data", {}).get("datasets", {}).get("items", [])
        filtered = [d for d in datasets if d.get("createdBy", {}).get("email") == creator_email]
        return {
            "datasets": filtered,
            "count": len(filtered),
            "current_page": page,
            "per_page": per_page,
        }
    except Exception as e:
        return {"error": f"Failed to list datasets by creator: {str(e)}"}


@mcp.tool
def preview_dataset_file(file_id: str) -> dict:
    """
    Preview a dataset file by fetching a sample using the OpenHEXA GraphQL API.
    Args:
        file_id: The ID of the file to preview
    Returns:
        Dict containing the file sample, status, and any status reason
    """
    if not OPENHEXA_AVAILABLE:
        return {"error": "OpenHEXA SDK not available. Please configure your OpenHEXA credentials."}
    try:
        query = """
        query GetDatasetVersionFileSample($id: ID!) {
          datasetVersionFile(id: $id) {
            id
            properties
            fileSample {
              sample
              status
              statusReason
              __typename
            }
            __typename
          }
        }
        """
        variables = {"id": file_id}
        result = openhexa.execute(query=query, variables=variables)
        response_data = result.json()
        if "errors" in response_data:
            return {"error": f"GraphQL error: {response_data['errors']}", "raw": response_data}
        file_data = response_data.get("data", {}).get("datasetVersionFile")
        if not file_data:
            return {"error": f"File '{file_id}' not found"}
        sample_info = file_data.get("fileSample")
        return {
            "file_id": file_id,
            "sample": sample_info.get("sample") if sample_info else None,
            "status": sample_info.get("status") if sample_info else None,
            "status_reason": sample_info.get("statusReason") if sample_info else None,
            "properties": file_data.get("properties"),
        }
    except Exception as e:
        return {"error": f"Failed to preview file: {str(e)}"}


def main():
    """Main entry point for the MCP OpenHEXA server."""
    # Check for required environment variables or configuration
    if not OPENHEXA_AVAILABLE:
        print("Warning: OpenHEXA SDK not properly initialized", file=sys.stderr)
        print("The server will start but tools will return configuration errors", file=sys.stderr)
        print(
            "Please configure your OpenHEXA credentials (HEXA_SERVER_URL, HEXA_TOKEN)",
            file=sys.stderr,
        )

    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()
