interface PathType {
  d: string;
  fill?: string;
}

interface SvgIconProps {
  xmlns?: string;
  width?: string | number;
  height?: string | number;
  viewBox?: string;
  fill?: string;
  className?: string;
  paths?: PathType[];
}

const SvgIcon: React.FC<SvgIconProps> = ({
  xmlns = "http://www.w3.org/2000/svg",
  width = "21",
  height = "21",
  viewBox = "0 0 21 21",
  fill = "none",
  className = "",
  paths = [],
}) => {
  return (
    <svg
      xmlns={xmlns}
      width={width}
      height={height}
      viewBox={viewBox}
      fill={fill}
      className={className}
    >
      {paths.map((path, index) => (
        <path key={index} d={path.d} fill={path.fill || fill} />
      ))}
    </svg>
  );
};

export default SvgIcon;