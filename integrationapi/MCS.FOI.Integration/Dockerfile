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

COPY fonts/ /usr/share/fonts/truetype/
RUN apt-get update && apt-get install -y --no-install-recommends fontconfig
RUN fc-cache -f -v
# Install required native dependencies for SkiaSharp
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfontconfig1 \
    libfreetype6 \
    libpng16-16 \
    libjpeg62-turbo \
    libwebpdemux2 \
    libtiff6 \
    libgif7 \
    libglib2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libharfbuzz0b \
    libfribidi0 \
    libicu-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container.
WORKDIR /app

# Copy the published output from the build stage.
COPY --from=build /src/MCS.FOI.Integration.API/out ./

# copy app data to the image.
# requires a manual copy from /app/app-data to the PVC /app/App_Data
COPY MCS.FOI.Integration.API/App_Data/. /app/app-data/
# COPY MCS.FOI.Integration.API/App_Data/. /app/App_Data/

# Expose the port that the application listens on.
EXPOSE 8080

# Specify the entry point for the application.
ENTRYPOINT ["dotnet", "MCS.FOI.Integration.API.dll"]