namespace MCS.FOI.Integration.Infrastructure
{
    public static class DependencyInjection
    {
        public static IServiceCollection AddInfrastructureServices(this IServiceCollection services, IConfiguration configuration)
        {
            services.AddDbContext<IntegrationDbContext>(options =>
                    options.UseNpgsql(configuration.GetConnectionString("DBConnection"),
                        npgsqlOptions =>
                        {
                            npgsqlOptions.EnableRetryOnFailure();
                        }).EnableDetailedErrors());

            // Register Redis ConnectionMultiplexer
            services.AddSingleton<ConnectionMultiplexer>(sp =>
            {
                var redisConnection = configuration.GetConnectionString("Redis");

                if (string.IsNullOrWhiteSpace(redisConnection))
                {
                    Console.WriteLine("Redis connection string is missing. Redis will be ignored.");
                    return null;
                }

                try
                {
                    var config = ConfigurationOptions.Parse(redisConnection, true);
                    var connection = ConnectionMultiplexer.Connect(config);

                    if (connection.IsConnected)
                    {
                        Console.WriteLine("Redis connected successfully.");
                        return connection;
                    }

                    Console.WriteLine("Redis is not connected. Redis will be ignored.");
                    connection.Dispose();
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Redis connection failed: {ex.Message}. Redis will be ignored.");
                }

                return null;
            });

            // Register Redis Context
            services.AddSingleton<IRedisDbContext>(sp =>
            {
                var connection = sp.GetService<ConnectionMultiplexer>();
                return connection != null && connection.IsConnected
                ? new RedisDbContext(connection)
                    : new RedisDbContext(null);
            });

            services.AddTransient<IRedisDbContext, RedisDbContext>();
            services.AddScoped(typeof(IRedisRepository<>), typeof(RedisRepository<>));
            services.AddScoped<IDapperRepository, DapperRepository>();

            return services;
        }
    }
}
