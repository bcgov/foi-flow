using MCS.FOI.Integration.Application.Services.TemplateDataService;
using MCS.FOI.Integration.Core.DTOs;
using MCS.FOI.Integration.Core.Repositories.Base;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;

namespace MCS.FOI.Integration.Tests;

[TestClass]
public class TemplateDataServiceTests
{
    [TestMethod]
    public async Task UpdateTemplates_UsesCorrectDatabaseColumnsAndParameters()
    {
        var repository = new Mock<IDapperRepository>(MockBehavior.Strict);

        repository.Setup(x => x.UpdateAsync<TemplateDto>(
                It.IsAny<string>(),
                It.IsAny<IEnumerable<TemplateDto>>()))
            .Returns(Task.CompletedTask);

        var service = new TemplateDataService(repository.Object);

        var template = new TemplateDto
        {
            TemplateId = 105,
            FileName = "AConsultRequest",
            EncodedContent = "TkVX"
        };

        await service.UpdateTemplates(new[] { template });

        repository.Verify(x => x.UpdateAsync<TemplateDto>(
            It.Is<string>(sql =>
                sql.Contains("SET encodedcontent = @EncodedContent") &&
                sql.Contains("WHERE templateid = @TemplateId")),
            It.Is<IEnumerable<TemplateDto>>(items =>
                items.Single().TemplateId == 105)),
            Times.Once());
    }
}
