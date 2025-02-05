namespace MCS.FOI.Integration.Application.Queries.GetListOptions
{
    public class GetListOptionsQuery: IQuery<IEnumerable<ListOptionsResult>>{}

    public class ListOptionsResult
    {
        public int Id { get; set; }
        public string Code { get; set; } = default!;
        public string Description { get; set; } = default!;
    }
}
