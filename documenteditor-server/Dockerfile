FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
WORKDIR /app
EXPOSE 80
ENV SYNCFUSION_LICENSE_KEY=""
ENV SPELLCHECK_DICTIONARY_PATH=""
ENV SPELLCHECK_JSON_FILENAME=""
ENV SPELLCHECK_CACHE_COUNT=""
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build

WORKDIR /source
COPY ["src/EJ2APIServices_NET8.csproj", "./EJ2APIServices_NET8.csproj"]
COPY ["src/NuGet.Config", "./"]
RUN dotnet restore "./EJ2APIServices_NET8.csproj"
COPY . .
WORKDIR "/source/src"
RUN dotnet build -c Release -o /app

FROM build AS publish
RUN dotnet publish -c Release -o /app

FROM base AS final
WORKDIR /app
COPY --from=publish /app .
ENTRYPOINT ["dotnet", "EJ2APIServices_NET8.dll"]