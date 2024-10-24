import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  FormControl,
  FormLabel,
  Input,
  Button,
  Select,
  Box,
  VStack,
  Heading,
  SimpleGrid,
  Switch,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Text,
  useDisclosure,
} from "@chakra-ui/react";
import { getDonor, updateDonor } from "./API";
import { toast } from "react-toastify";
import LoadingBubbles from "./components/LoadingBubbles";

const Home = () => {
  const { donorId } = useParams();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [error, setError] = useState(null);
  const [geoEnabled, setGeoEnabled] = useState(true);

  const handleShareLocation = () => {
    if (!navigator.geolocation) {
      setGeoEnabled(false);
      toast.error("Sorry! Geolocation is not supported by this browser.");
      setError("Geolocation is not supported by this browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        setDonorData({
          ...donorData,
          latitude: lat,
          longitude: lon,
        });
        toast.success(`Location successfuly grabbed as ${lat}°N, ${lon}°E`);
        setError(null);
      },
      (err) => {
        if (err.code === err.PERMISSION_DENIED) {
          toast.error(
            "Please enable location services in your browser settings."
          );
          setError("Please enable location services in your browser settings.");
        } else {
          setError(err.message);
        }
      }
    );
  };

  const bloodGroups = [
    { value: "O+", label: "O+", bgColor: "red.100" },
    { value: "O-", label: "O-", bgColor: "yellow.100" },
    { value: "A+", label: "A+", bgColor: "blue.100" },
    { value: "A-", label: "A-", bgColor: "green.100" },
    { value: "B+", label: "B+", bgColor: "orange.100" },
    { value: "B-", label: "B-", bgColor: "purple.100" },
    { value: "AB+", label: "AB+", bgColor: "pink.100" },
    { value: "AB-", label: "AB-", bgColor: "teal.100" },
  ];

  const [donorData, setDonorData] = useState({
    name: "",
    firstName: "",
    lastName: "",
    chatPlatform: "",
    telegramUsername: "",
    discordUserId: "",
    telegramChatId: "",
    latitude: null,
    longitude: null,
    lastDonated: "",
    bloodGroup: "",
    isNotificationDisabled: false,
  });

  useEffect(() => {
    const fetchDonor = async () => {
      try {
        const data = await getDonor(donorId);
        if (data.ERROR) {
          return;
        }
        setDonorData(data);
      } catch (error) {
        console.error("Error fetching donor data:", error);
      }
    };

    if (donorId) {
      fetchDonor();
    }
  }, [donorId]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setDonorData({
      ...donorData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSwitchChange = (e) => {
    setDonorData({ ...donorData, isNotificationDisabled: e.target.checked });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const x = donorData;
      if (
        x.latitude == null ||
        x.longitude == null ||
        x.bloodGroup == null ||
        x.bloodGroup == ""
      ) {
        let desc = "Error";
        if (x.latitude == null || x.longitude == null) {
          desc = "Please share your current location...";
        } else if (x.bloodGroup == null || x.bloodGroup == "") {
          desc = "Please fill up your blood-group...";
        }
        toast.error(`${desc}`);
        return;
      }
      const updatedData = {
        latitude: donorData.latitude,
        longitude: donorData.longitude,
        lastDonated: donorData.lastDonated,
        bloodGroup: donorData.bloodGroup,
        isNotificationDisabled: donorData.isNotificationDisabled,
      };
      const data = await updateDonor(donorId, updatedData);
      if (data.ERROR) {
        return;
      }
      toast.success("Donor info updated successfully!");
      onOpen(); // Open the success modal
    } catch (error) {
      console.error("Error updating donor data:", error);
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return "";
    return isoString.split("T")[0];
  };

  if (donorData.name === "") {
    return <LoadingBubbles />;
  }

  return (
    <>
      <Box
        maxW="600px"
        mx="auto"
        mt={10}
        p={6}
        boxShadow="xl"
        borderRadius="md"
        bg="white"
        _dark={{ bg: "gray.800" }}
      >
        <VStack spacing={6}>
          <Heading as="h2" size="lg" mb={6} textAlign="center">
            Donor Information
          </Heading>

          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
            <FormControl isRequired>
              <FormLabel>Name</FormLabel>
              <Input
                type="text"
                name="name"
                value={donorData.name}
                onChange={handleInputChange}
                isDisabled
                placeholder="Enter full name"
                sx={{
                  opacity: 0.9,
                  color: "gray.800",
                  backgroundColor: "gray.100",
                  cursor: "not-allowed",
                  _disabled: {
                    borderColor: "gray.400",
                  },
                }}
              />
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Chat Platform</FormLabel>
              <Select
                name="chatPlatform"
                value={donorData.chatPlatform}
                onChange={handleInputChange}
                isDisabled
                placeholder="Select Chat Platform"
                sx={{
                  opacity: 0.9,
                  color: "gray.800",
                  backgroundColor: "gray.100",
                  cursor: "not-allowed",
                  _disabled: {
                    borderColor: "gray.400",
                  },
                }}
              >
                <option value="telegram">Telegram</option>
                <option value="discord">Discord</option>
              </Select>
            </FormControl>
          </SimpleGrid>

          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
            <FormControl isRequired>
              <FormLabel>Your Location</FormLabel>
              <Button onClick={handleShareLocation} colorScheme="green" mt={0}>
                Share Current Location
              </Button>
            </FormControl>

            <FormControl>
              <FormLabel>Last Donated</FormLabel>
              <Input
                type="date"
                name="lastDonated"
                value={formatDate(donorData.lastDonated)}
                onChange={handleInputChange}
              />
            </FormControl>
          </SimpleGrid>

          <FormControl isRequired>
            <FormLabel>Blood Group</FormLabel>
            <SimpleGrid columns={4} spacing={4}>
              {bloodGroups.map((group) => (
                <Button
                  key={group.value}
                  onClick={() =>
                    handleInputChange({
                      target: {
                        name: "bloodGroup",
                        value: group.value,
                        type: "button",
                      },
                    })
                  }
                  bg={
                    donorData.bloodGroup === group.value
                      ? "black"
                      : group.bgColor
                  }
                  color={
                    donorData.bloodGroup === group.value ? "white" : "black"
                  }
                  _hover={
                    donorData.bloodGroup === group.value
                      ? { bg: "black" }
                      : { bg: `${group.bgColor.split(".")[0]}.300` }
                  }
                  _active={
                    donorData.bloodGroup === group.value
                      ? { bg: "black" }
                      : { bg: `${group.bgColor.split(".")[0]}.400` }
                  }
                  isActive={donorData.bloodGroup === group.value}
                  border={
                    donorData.bloodGroup === group.value
                      ? "2px solid black"
                      : "none"
                  }
                >
                  {group.label}
                </Button>
              ))}
            </SimpleGrid>
          </FormControl>

          <Button colorScheme="teal" size="lg" w="full" onClick={handleSubmit}>
            Submit Donor Info
          </Button>
        </VStack>
      </Box>

      {/* Success Modal */}
      <Modal isOpen={isOpen} onClose={onClose} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader textAlign="center">Success!</ModalHeader>
          <ModalBody>
            <Text textAlign="center" fontSize="lg">
              Thanks! Your info has been saved. You may now go back to{" "}
              {donorData["chatPlatform"]}.
            </Text>
          </ModalBody>
          <ModalFooter justifyContent="center">
            <Button colorScheme="teal" onClick={onClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default Home;
