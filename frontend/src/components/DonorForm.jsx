import React, { useState } from "react";
import {
  Box,
  FormControl,
  FormLabel,
  Input,
  Button,
  Select,
  Text,
  Switch,
  useToast,
  VStack,
  Stack,
  Heading,
  SimpleGrid,
} from "@chakra-ui/react";

const DonorForm = () => {
  const [donorData, setDonorData] = useState({
    name: "",
    firstName: "",
    lastName: "",
    chatPlatform: "",
    telegramUsername: "",
    discordUserId: "",
    telegramChatId: "",
    latitude: "",
    longitude: "",
    lastDonated: "",
    bloodGroup: "",
    isNotificationDisabled: false,
  });

  const toast = useToast();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setDonorData({ ...donorData, [name]: value });
  };

  const handleSwitchChange = (e) => {
    setDonorData({ ...donorData, isNotificationDisabled: e.target.checked });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/donor", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(donorData),
      });

      if (response.ok) {
        toast({
          title: "Donor created successfully.",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
        setDonorData({
          name: "",
          firstName: "",
          lastName: "",
          chatPlatform: "",
          telegramUsername: "",
          discordUserId: "",
          telegramChatId: "",
          latitude: "",
          longitude: "",
          lastDonated: "",
          bloodGroup: "",
          isNotificationDisabled: false,
        });
      } else {
        throw new Error("Failed to create donor");
      }
    } catch (error) {
      toast({
        title: "Error creating donor.",
        description: error.message,
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
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
            <FormLabel>Full Name</FormLabel>
            <Input
              type="text"
              name="name"
              value={donorData.name}
              onChange={handleInputChange}
              placeholder="Enter full name"
            />
          </FormControl>

          <FormControl>
            <FormLabel>First Name</FormLabel>
            <Input
              type="text"
              name="firstName"
              value={donorData.firstName}
              onChange={handleInputChange}
              placeholder="First Name (Optional)"
            />
          </FormControl>

          <FormControl>
            <FormLabel>Last Name</FormLabel>
            <Input
              type="text"
              name="lastName"
              value={donorData.lastName}
              onChange={handleInputChange}
              placeholder="Last Name (Optional)"
            />
          </FormControl>

          <FormControl isRequired>
            <FormLabel>Chat Platform</FormLabel>
            <Select
              name="chatPlatform"
              value={donorData.chatPlatform}
              onChange={handleInputChange}
              placeholder="Select Chat Platform"
            >
              <option value="Telegram">Telegram</option>
              <option value="Discord">Discord</option>
            </Select>
          </FormControl>
        </SimpleGrid>

        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
          <FormControl>
            <FormLabel>Telegram Username</FormLabel>
            <Input
              type="text"
              name="telegramUsername"
              value={donorData.telegramUsername}
              onChange={handleInputChange}
              placeholder="Telegram Username"
            />
          </FormControl>

          <FormControl>
            <FormLabel>Discord User ID</FormLabel>
            <Input
              type="text"
              name="discordUserId"
              value={donorData.discordUserId}
              onChange={handleInputChange}
              placeholder="Discord User ID"
            />
          </FormControl>

          <FormControl>
            <FormLabel>Telegram Chat ID</FormLabel>
            <Input
              type="text"
              name="telegramChatId"
              value={donorData.telegramChatId}
              onChange={handleInputChange}
              placeholder="Telegram Chat ID"
            />
          </FormControl>
        </SimpleGrid>

        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
          <FormControl>
            <FormLabel>Latitude</FormLabel>
            <Input
              type="number"
              name="latitude"
              value={donorData.latitude}
              onChange={handleInputChange}
              placeholder="Latitude"
            />
          </FormControl>

          <FormControl>
            <FormLabel>Longitude</FormLabel>
            <Input
              type="number"
              name="longitude"
              value={donorData.longitude}
              onChange={handleInputChange}
              placeholder="Longitude"
            />
          </FormControl>

          <FormControl>
            <FormLabel>Last Donated</FormLabel>
            <Input
              type="date"
              name="lastDonated"
              value={donorData.lastDonated}
              onChange={handleInputChange}
            />
          </FormControl>

          <FormControl isRequired>
            <FormLabel>Blood Group</FormLabel>
            <Select
              name="bloodGroup"
              value={donorData.bloodGroup}
              onChange={handleInputChange}
              placeholder="Select Blood Group"
            >
              <option value="O+">O+</option>
              <option value="O-">O-</option>
              <option value="A+">A+</option>
              <option value="A-">A-</option>
              <option value="B+">B+</option>
              <option value="B-">B-</option>
              <option value="AB+">AB+</option>
              <option value="AB-">AB-</option>
            </Select>
          </FormControl>
        </SimpleGrid>

        <FormControl display="flex" alignItems="center">
          <FormLabel mb="0">Disable Notifications</FormLabel>
          <Switch
            isChecked={donorData.isNotificationDisabled}
            onChange={handleSwitchChange}
          />
        </FormControl>

        <Button colorScheme="teal" size="lg" w="full" onClick={handleSubmit}>
          Submit Donor Info
        </Button>
      </VStack>
    </Box>
  );
};

export default DonorForm;
