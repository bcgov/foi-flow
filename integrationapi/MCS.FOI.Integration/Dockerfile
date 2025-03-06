# Use the official .NET SDK image as a parent image.
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

# Set the working directory in the container.
WORKDIR /src
COPY ["MCS.FOI.Integration.sln", "./"]

# Copy the .csproj files and restore any dependencies (NuGet packages).
#COPY **/*.csproj ./
COPY ["MCS.FOI.Integration.API/MCS.FOI.Integration.API.csproj", "MCS.FOI.Integration.API/"]
COPY ["MCS.FOI.Integration.Application/MCS.FOI.Integration.Application.csproj", "MCS.FOI.Integration.Application/"]
COPY ["MCS.FOI.Integration.Core/MCS.FOI.Integration.Core.csproj", "MCS.FOI.Integration.Core/"]
COPY ["MCS.FOI.Integration.Infrastructure/MCS.FOI.Integration.Infrastructure.csproj", "MCS.FOI.Integration.Infrastructure/"]
RUN dotnet restore "MCS.FOI.Integration.sln"

# Copy the remaining files and build the application.
COPY . .
WORKDIR "/src/MCS.FOI.Integration.API"
RUN dotnet publish -c Release -o out

# Use the official .NET runtime image as a base image for the final stage.
FROM mcr.microsoft.com/dotnet/aspnet:8.0

# Set the working directory in the container.
WORKDIR /app

# Copy the published output from the build stage.
COPY --from=build /src/MCS.FOI.Integration.API/out ./

# copy app data to the image.
COPY MCS.FOI.Integration.API/App_Data /app-data/
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Expose the port that the application listens on.
EXPOSE 8080

# Specify the entry point for the application.
ENTRYPOINT ["/app/entrypoint.sh"]