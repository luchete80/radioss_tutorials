#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <filesystem>
#include <sstream>
#include <regex>
#include <cstring>

namespace fs = std::filesystem;

// Function to find the start index of the first integer substring
int find_integer_substring_index(const std::string& str) {
    for (size_t i = 0; i < str.size(); ++i) {
        if (isdigit(str[i])) {
            return i;
        }
    }
    return -1;
}

// Function to find the end index of the integer substring
int find_integer_substring_end_index(const std::string& str) {
    for (int i = str.size() - 1; i >= 0; --i) {
        if (isdigit(str[i])) {
            return i;
        }
    }
    return -1;
}

// Convert substring to integer
int convert_substring_to_integer(const std::string& str, int start, int end) {
    if (start != -1 && end != -1 && start <= end) {
        try {
            return std::stoi(str.substr(start, end - start + 1));
        } catch (const std::invalid_argument& e) {
            std::cerr << "Error: The substring cannot be converted to an integer." << std::endl;
        } catch (const std::out_of_range& e) {
            std::cerr << "Error: Integer value out of range." << std::endl;
        }
    }
    return -1;
}

// Write force data to CSV file
void write_list(const std::vector<std::vector<double>>& force, int mesh, int tool) {
    std::ofstream fi_x("force_m" + std::to_string(mesh) + "_t_" + std::to_string(tool) + ".csv");
    if (!fi_x.is_open()) {
        std::cerr << "Error opening output file." << std::endl;
        return;
    }

    fi_x << "t,fx,fy,fz\n";
    double dt = 1.0e-3;
    double t = 0.0;

    for (const auto& f : force) {
        fi_x << t << ", " << f[0] << ", " << f[1] << ", " << f[2] << "\n";
        std::cout << f[0] << ", " << f[1] << ", " << f[2] << std::endl;
        t += dt;
    }
}

std::vector<std::vector<double>> open_files_with_extension(const std::string& directory, const std::string& extension) {
    if (!fs::exists(directory) || !fs::is_directory(directory)) {
        std::cerr << "Directory '" << directory << "' does not exist." << std::endl;
        return {};
    }

    std::vector<fs::path> files;
    for (const auto& entry : fs::directory_iterator(directory)) {
        if (entry.path().extension() == extension) {
            files.push_back(entry.path());
        }
    }

    if (files.empty()) {
        std::cerr << "No files found with '" << extension << "' extension in '" << directory << "'." << std::endl;
        return {};
    }

    std::cout << "Found " << files.size() << " files" << std::endl;
    std::vector<std::vector<double>> force(files.size(), std::vector<double>(3, 0.0));
    bool first = true;
    size_t node_count = 0;

    for (size_t j = 0; j < files.size(); ++j) {
        const auto& file_path = files[j];
        std::string file_name = file_path.filename().string();

        int start_idx = find_integer_substring_index(file_name);
        int end_idx = find_integer_substring_end_index(file_name);
        int idx = convert_substring_to_integer(file_name, start_idx, end_idx);

        std::ifstream file(file_path);
        if (!file.is_open()) {
            std::cerr << "Error opening " << file_name << std::endl;
            continue;
        }

        std::cout << "File " << file_name << " found" << std::endl;
        std::vector<std::string> lines;
        std::string line;
        while (std::getline(file, line)) {
            lines.push_back(line);
        }

        size_t line_ini = 0;
        if (first) {
            for (size_t i = 0; i < lines.size(); ++i) {
                if (lines[i].find("VECTORS Contact_Forces float") != std::string::npos) {
                    std::cout << "FOUND STRING in line " << i << ": " << lines[i] << std::endl;
                    line_ini = i + 1;
                    node_count = lines.size() - line_ini;
                    std::cout << "Node Count: " << node_count << std::endl;
                    first = false;
                    break;
                }
            }
        }

        for (size_t k = 0; k < node_count; ++k) {
            std::istringstream iss(lines[line_ini + k]);
            double num;
            size_t d = 0;
            while (iss >> num && d < 3) {
                force[idx][d++] += num;
            }
        }

        std::cout << "Contact Force in tool Node Range: [" << force[idx][0] << ", " << force[idx][1] << ", " << force[idx][2] << "]" << std::endl;
    }

    return force;
}

int main() {
    std::string directory = "./out/"; // Specify your directory
    std::string extension = ".txt";   // Specify the file extension
    auto forces = open_files_with_extension(directory, extension);
    write_list(forces, 1, 1); // Example call with mesh = 1, tool = 1
    return 0;
}
