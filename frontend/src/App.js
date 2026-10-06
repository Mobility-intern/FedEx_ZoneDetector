import React, { useState, useEffect } from "react";
import {
  Layout,
  Select,
  Input,
  Button,
  Typography,
  Spin,
  message,
  Switch,
} from "antd";
import "antd/dist/reset.css";
import {
  BulbOutlined,
  MoonOutlined,
  EnvironmentOutlined,
  SafetyCertificateOutlined,
  WarningOutlined,
} from "@ant-design/icons";
import "./App.css";

const { Header, Content } = Layout;
const { Title, Text } = Typography;
const { Option } = Select;

// Normalize zone names
const ZONE_NAME_MAP = {
  "Airport Yellow(5-8Km)": "Airport Yellow [5-8] km",
  "Airport Yellow(8-12Km)": "Airport Yellow [8-12] km",
  "Green Zone": "Green Zone",
};

const zoneColors = {
  "Airport Red": "rgb(232, 118, 124)",
  "Airport Yellow [5-8] km": "rgb(237, 237, 154)",
  "Airport Yellow [8-12] km": "rgb(230, 230, 147)",
  "Red Zone": "rgb(237, 26, 2)",
  "Airspace - Red Zone": "rgb(255, 100, 100)",
  "Temporary Red Zone": "rgb(235, 123, 108)",
  "Green Zone": "green",
};

const SAFE_ZONES = [
  "Green Zone",
  "Airport Yellow [5-8] km",
  "Airport Yellow [8-12] km",
];

const normalizeZoneName = (zone) =>
  ZONE_NAME_MAP[zone?.trim()] || zone?.trim() || "Green Zone";

const App = () => {
  const [searchType, setSearchType] = useState("coordinates");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [zones, setZones] = useState([]);
  const [rawZones, setRawZones] = useState([]);
  const [imageSrc, setImageSrc] = useState(null);
  const [isDark, setIsDark] = useState(true);
  const [shake, setShake] = useState(false);

  // Apply theme to body
  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      isDark ? "dark" : "light"
    );
  }, [isDark]);

  const detectZone = async () => {
    if (!input.trim()) {
      setShake(true);
      message.warning("Please enter a valid input.");
      setTimeout(() => setShake(false), 500);
      return;
    }

    // Validation for coordinates
    if (searchType === "coordinates") {
      // Regex allows: optional minus, digits, optional decimal, comma, optional space, optional minus, digits, optional decimal
      const coordRegex = /^-?\d+(\.\d+)?,\s*-?\d+(\.\d+)?$/;
      if (!coordRegex.test(input.trim())) {
        setShake(true);
        message.error("enter right one...");
        setTimeout(() => setShake(false), 500);
        return;
      }
    }

    setLoading(true);
    setZones([]);
    setRawZones([]);
    setImageSrc(null);

    const queryParam =
      searchType === "coordinates"
        ? `coordinates=${encodeURIComponent(input)}`
        : `location=${encodeURIComponent(input)}`;

    try {
      const res = await fetch(
        `http://localhost:8000/detect_zones?${queryParam}`
      );
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || "Unknown error");

      setZones(data.zones_info || []);
      setRawZones(data.zones || []);
      setImageSrc(data.screenshot_uri || null);
    } catch (err) {
      message.error(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const allZoneTypes = [
    ...new Set(
      [
        ...zones.map((z) => normalizeZoneName(z?.zone_detail)),
        ...rawZones.map((z) => normalizeZoneName(z)),
      ].filter((type) => type && type !== "-")
    ),
  ];

  const isOnlySafeZones =
    allZoneTypes.length > 0 &&
    allZoneTypes.every((type) => SAFE_ZONES.includes(type));

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="header-left">
          <img src="/FedEx.png" alt="FedEx" height="36" />
        </div>

        <div className="header-center">
          <Title level={3} className="app-title">
            AIRSPACE GUARDIAN
          </Title>
        </div>

        <div className="header-right">
          <Switch
            checked={isDark}
            onChange={() => setIsDark(!isDark)}
            checkedChildren={<MoonOutlined />}
            unCheckedChildren={<BulbOutlined />}
            className="theme-switch"
          />
          <div className="amber-logo-container">
            <img src="/Amber_logo.avif" alt="Amberwings" height="28" />
          </div>
        </div>
      </Header>

      <Content className="app-content">
        <div className="search-container">
          <div className="search-header">
            <h2>FLIGHT ZONE SCANNER</h2>
            <p>Secure Airspace Verification System</p>
          </div>

          <div className={`search-inputs ${shake ? "shake" : ""}`}>
            <Select
              value={searchType}
              onChange={setSearchType}
              className="custom-select"
            >
              <Option value="coordinates">
                <EnvironmentOutlined
                  style={{ marginRight: 8, color: "var(--text-secondary)" }}
                />
                COORDINATES
              </Option>
              <Option value="keyword">
                <EnvironmentOutlined
                  style={{ marginRight: 8, color: "var(--text-secondary)" }}
                />
                LOCATION
              </Option>
            </Select>

            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                searchType === "coordinates"
                  ? "LAT, LONG (e.g., 12.9716, 77.5946)"
                  : "ENTER LOCATION NAME"
              }
              onPressEnter={detectZone}
              className="custom-input"
              prefix={
                <EnvironmentOutlined
                  style={{ color: "var(--text-secondary)", fontSize: "1.2rem" }}
                />
              }
            />

            <Button
              type="primary"
              onClick={detectZone}
              loading={loading}
              className="primary-button"
            >
              SCAN ZONE
            </Button>
          </div>
        </div>

        {loading && (
          <div style={{ textAlign: "center", marginTop: 60 }}>
            <Spin size="large" />
          </div>
        )}

        {!loading && (zones.length > 0 || rawZones.length > 0 || imageSrc) && (
          <div className="results-container">
            {/* Zone Info Card */}
            <div className="zone-info-card">
              <div style={{ marginBottom: "2rem" }}>
                <div className="section-title">
                  <SafetyCertificateOutlined
                    style={{ color: "var(--primary-color)" }}
                  />
                  DETECTED ZONES
                </div>
                <div className="tags-container">
                  {allZoneTypes.map((type, idx) => {
                    const lightType =
                      type.includes("Yellow") || type.includes("Temporary");
                    return (
                      <span
                        key={idx}
                        className="custom-tag"
                        style={{
                          backgroundColor:
                            zoneColors[type] || "rgba(255,255,255,0.1)",
                          color: lightType ? "#000" : "#fff",
                          border: `1px solid ${
                            zoneColors[type] || "rgba(255,255,255,0.2)"
                          }`,
                        }}
                      >
                        {type}
                      </span>
                    );
                  })}
                </div>
              </div>

              {/* Zone Details List */}
              {!isOnlySafeZones && zones.length > 0 && (
                <>
                  <div className="section-title">
                    <WarningOutlined style={{ color: "var(--accent-color)" }} />
                    RESTRICTED AREAS
                  </div>
                  <div className="zone-list">
                    {zones
                      .filter(
                        (zone) =>
                          !SAFE_ZONES.includes(
                            normalizeZoneName(zone?.zone_detail)
                          )
                      )
                      .map((zone, index) => {
                        const type = normalizeZoneName(zone?.zone_detail);
                        const lightType =
                          type.includes("Yellow") ||
                          type.includes("Temporary") ||
                          type === "Green Zone";
                        return (
                          <div key={index} className="zone-item">
                            <span
                              className="custom-tag"
                              style={{
                                backgroundColor:
                                  zoneColors[type] || "rgba(255,255,255,0.1)",
                                color: lightType ? "#000" : "#fff",
                                fontSize: "0.75rem",
                                padding: "0.2rem 0.6rem",
                                border: "none",
                              }}
                            >
                              {type}
                            </span>
                            <span className="zone-name">
                              {zone?.zone_name || "N/A"}
                            </span>
                          </div>
                        );
                      })}
                  </div>
                </>
              )}
            </div>

            {/* Map Screenshot */}
            {imageSrc && (
              <div className="map-container">
                <img
                  src={imageSrc}
                  alt="Map Screenshot"
                  className="map-image"
                />
              </div>
            )}
          </div>
        )}
      </Content>
    </Layout>
  );
};

export default App;
