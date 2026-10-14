using MCS.FOI.Integration.Application.Commands.UpdateRedisTemplate;
using MCS.FOI.Integration.Application.Services.S3Connection;
using MCS.FOI.Integration.Application.Services.TemplateDataService;
using MCS.FOI.Integration.Core.DTOs;
using MCS.FOI.Integration.Core.Repositories.RedisRepository;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;

namespace MCS.FOI.Integration.Tests;

[TestClass]
public class UpdateTemplateCacheTests
{
    private readonly Mock<IS3ConnectionService> _s3 = new(MockBehavior.Strict);
    private readonly Mock<ITemplateDataService> _data = new(MockBehavior.Strict);
    private readonly Mock<ITemplateRedisCacheRepository> _cache = new(MockBehavior.Strict);

    private TemplateDto _template = null!;
    private UpdateTemplateCacheCommandHandler _handler = null!;

    [TestInitialize]
    public void Initialize()
    {
        _template = new TemplateDto
        {
            TemplateId = 105,
            FileName = "AConsultRequest",
            TemplateName = "A - Consult - Request",
            DocumentPath = "/TEMPLATES/EMAILS/SYNCFUSION/A - Consult - Request.docx",
            Extension = ".docx",
            EncodedContent = "T0xE",
            IsActive = true,
            TemplateType = "letter",
            RequestType = "Both"
        };

        _data.Setup(x => x.GetAllTemplates())
            .ReturnsAsync((IEnumerable<TemplateDto>)new[] { _template });

        _s3.Setup(x => x.FetchTemplatesAsync(
                It.IsAny<string>(),
                It.IsAny<string>(),
                It.IsAny<string>(),
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<TemplateInfo>
            {
                new TemplateInfo
                {
                    Value = "AConsultRequest",
                    TemplateId = "test-template-id",
                    Text = "TkVX"
                }
            });

        _data.Setup(x => x.UpdateTemplates(
                It.IsAny<IEnumerable<TemplateDto>>()))
            .Returns(Task.CompletedTask);

        _cache.Setup(x => x.UpdateCacheTemplateAsync(
                It.IsAny<IEnumerable<TemplateDto>>()))
            .Returns(Task.CompletedTask);

        _handler = new UpdateTemplateCacheCommandHandler(
            _s3.Object, _cache.Object, _data.Object);
    }

    private Task<bool> RefreshAsync()
    {
        return _handler.Handle(
            new UpdateTemplateCacheCommand { Token = "unit-test-token" },
            CancellationToken.None);
    }

    [TestMethod]
    public async Task Refresh_UpdatesDatabaseAndRedisWithNewContent()
    {
        var result = await RefreshAsync();

        Assert.IsTrue(result);
        Assert.AreEqual("TkVX", _template.EncodedContent);

        _data.Verify(x => x.UpdateTemplates(
            It.Is<IEnumerable<TemplateDto>>(items =>
                items.Single().EncodedContent == "TkVX")),
            Times.Once());

        _cache.Verify(x => x.UpdateCacheTemplateAsync(
            It.Is<IEnumerable<TemplateDto>>(items =>
                items.Single().EncodedContent == "TkVX")),
            Times.Once());
    }

    [TestMethod]
    public async Task Refresh_EmptyS3Response_PreventsPersistence()
    {
        _s3.Setup(x => x.FetchTemplatesAsync(
                It.IsAny<string>(),
                It.IsAny<string>(),
                It.IsAny<string>(),
                It.IsAny<CancellationToken>()))
            .ReturnsAsync(new List<TemplateInfo>());

        await Assert.ThrowsExceptionAsync<InvalidOperationException>(
            async () => { await RefreshAsync(); });

        Assert.AreEqual("T0xE", _template.EncodedContent);

        _data.Verify(x => x.UpdateTemplates(
            It.IsAny<IEnumerable<TemplateDto>>()), Times.Never());

        _cache.Verify(x => x.UpdateCacheTemplateAsync(
            It.IsAny<IEnumerable<TemplateDto>>()), Times.Never());
    }

    [TestMethod]
    public async Task Refresh_S3Exception_PreventsPersistence()
    {
        _s3.Setup(x => x.FetchTemplatesAsync(
                It.IsAny<string>(),
                It.IsAny<string>(),
                It.IsAny<string>(),
                It.IsAny<CancellationToken>()))
            .ThrowsAsync(new HttpRequestException("Simulated S3 failure"));

        await Assert.ThrowsExceptionAsync<HttpRequestException>(
            async () => { await RefreshAsync(); });

        _data.Verify(x => x.UpdateTemplates(
            It.IsAny<IEnumerable<TemplateDto>>()), Times.Never());

        _cache.Verify(x => x.UpdateCacheTemplateAsync(
            It.IsAny<IEnumerable<TemplateDto>>()), Times.Never());
    }

    [TestMethod]
    public async Task Refresh_DatabaseFailure_DoesNotUpdateRedis()
    {
        _data.Setup(x => x.UpdateTemplates(
                It.IsAny<IEnumerable<TemplateDto>>()))
            .ThrowsAsync(new InvalidOperationException(
                "Simulated database failure"));

        await Assert.ThrowsExceptionAsync<InvalidOperationException>(
            async () => { await RefreshAsync(); });

        _cache.Verify(x => x.UpdateCacheTemplateAsync(
            It.IsAny<IEnumerable<TemplateDto>>()), Times.Never());
    }

    [TestMethod]
    public async Task Refresh_RedisFailure_PropagatesException()
    {
        _cache.Setup(x => x.UpdateCacheTemplateAsync(
                It.IsAny<IEnumerable<TemplateDto>>()))
            .ThrowsAsync(new InvalidOperationException(
                "Simulated Redis failure"));

        await Assert.ThrowsExceptionAsync<InvalidOperationException>(
            async () => { await RefreshAsync(); });

        _data.Verify(x => x.UpdateTemplates(
            It.IsAny<IEnumerable<TemplateDto>>()), Times.Once());

        _cache.Verify(x => x.UpdateCacheTemplateAsync(
            It.IsAny<IEnumerable<TemplateDto>>()), Times.Once());
    }
}
