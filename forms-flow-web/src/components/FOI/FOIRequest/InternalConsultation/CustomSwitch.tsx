import "./CustomSwitch.scss";

type CustomSwitchProps = {
  checked: boolean;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
};

const CustomSwitch: React.FC<CustomSwitchProps> = ({ checked, onChange }) => {
  return (
    <label className="custom-switch">
      <input type="checkbox" checked={checked} onChange={onChange} className="visually-hidden"/>
      <span className="slider">
        <svg
            className="switch-handle"
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 21 21"
            fill="none"
            >
            <circle className="handle-circle" cx="10.5" cy="10.5" r="9" />
            </svg>
      </span>
    </label>
  );
};

export default CustomSwitch;